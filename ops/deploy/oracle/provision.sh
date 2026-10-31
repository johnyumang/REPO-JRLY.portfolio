#!/usr/bin/env bash
# Creates (or finds) the Oracle Always Free network + ARM VM and boots it with install.sh.
# Idempotent: safe to run every 30 min — it exits early when the VM already exists.
# Needs the OCI CLI configured (~/.oci/config). Writes the public IP to $GITHUB_OUTPUT / stdout.
set -euo pipefail
NAME=jrly-medusa
C=$(awk -F= '/^tenancy/{gsub(/ /,"",$2);print $2}' ~/.oci/config)
q() { oci "$@" --compartment-id "$C" --all 2>/dev/null; }
out() { echo "$1=$2"; [ -n "${GITHUB_OUTPUT:-}" ] && echo "$1=$2" >> "$GITHUB_OUTPUT" || true; }

# --- Existing VM? -----------------------------------------------------------
ID=$(q compute instance list --display-name $NAME --lifecycle-state RUNNING --query 'data[0].id' --raw-output || true)
if [ -n "$ID" ] && [ "$ID" != "null" ]; then
  IP=$(oci compute instance list-vnics --instance-id "$ID" --query 'data[0]."public-ip"' --raw-output)
  echo "VM already running"; out ip "$IP"; out created false; exit 0
fi

# --- Network (VCN, internet gateway, route, public subnet, ports 22/80/443) --
VCN=$(q network vcn list --display-name jrly-vcn --query 'data[0].id' --raw-output || true)
if [ -z "$VCN" ] || [ "$VCN" = "null" ]; then
  echo "creating VCN"
  VCN=$(oci network vcn create --compartment-id "$C" --display-name jrly-vcn --cidr-blocks '["10.0.0.0/16"]' --dns-label jrly --wait-for-state AVAILABLE --query 'data.id' --raw-output)
fi
IGW=$(q network internet-gateway list --vcn-id "$VCN" --query 'data[0].id' --raw-output || true)
if [ -z "$IGW" ] || [ "$IGW" = "null" ]; then
  IGW=$(oci network internet-gateway create --compartment-id "$C" --vcn-id "$VCN" --is-enabled true --display-name jrly-igw --wait-for-state AVAILABLE --query 'data.id' --raw-output)
fi
RT=$(oci network vcn get --vcn-id "$VCN" --query 'data."default-route-table-id"' --raw-output)
oci network route-table update --rt-id "$RT" --force \
  --route-rules "[{\"destination\":\"0.0.0.0/0\",\"destinationType\":\"CIDR_BLOCK\",\"networkEntityId\":\"$IGW\"}]" >/dev/null
SL=$(oci network vcn get --vcn-id "$VCN" --query 'data."default-security-list-id"' --raw-output)
rule() { echo "{\"source\":\"0.0.0.0/0\",\"protocol\":\"6\",\"tcpOptions\":{\"destinationPortRange\":{\"min\":$1,\"max\":$1}}}"; }
oci network security-list update --security-list-id "$SL" --force \
  --ingress-security-rules "[$(rule 22),$(rule 80),$(rule 443)]" >/dev/null
SUB=$(q network subnet list --vcn-id "$VCN" --query 'data[0].id' --raw-output || true)
if [ -z "$SUB" ] || [ "$SUB" = "null" ]; then
  SUB=$(oci network subnet create --compartment-id "$C" --vcn-id "$VCN" --cidr-block 10.0.0.0/24 --display-name jrly-public --dns-label pub --wait-for-state AVAILABLE --query 'data.id' --raw-output)
fi

# --- Image + launch (tries every availability domain, then a smaller shape) --
IMG=$(oci compute image list --compartment-id "$C" --operating-system "Canonical Ubuntu" --operating-system-version "24.04" \
  --shape VM.Standard.A1.Flex --sort-by TIMECREATED --sort-order DESC --query 'data[0].id' --raw-output)
ADS=$(oci iam availability-domain list --compartment-id "$C" --query 'data[].name' --raw-output | tr -d '[]", ' | grep -v '^$')
for SIZE in '{"ocpus":2,"memoryInGBs":12}' '{"ocpus":1,"memoryInGBs":6}'; do
  for AD in $ADS; do
    echo "trying $AD $SIZE"
    if ID=$(oci compute instance launch --compartment-id "$C" --availability-domain "$AD" --display-name $NAME \
        --shape VM.Standard.A1.Flex --shape-config "$SIZE" --image-id "$IMG" --subnet-id "$SUB" --assign-public-ip true \
        --user-data-file "$USER_DATA" --wait-for-state RUNNING --query 'data.id' --raw-output 2>/tmp/launch.err); then
      IP=$(oci compute instance list-vnics --instance-id "$ID" --query 'data[0]."public-ip"' --raw-output)
      echo "launched $ID"; out ip "$IP"; out created true; exit 0
    fi
    grep -qi "capacity" /tmp/launch.err && echo "  out of capacity" || { cat /tmp/launch.err; exit 1; }
  done
done
echo "All availability domains are out of ARM capacity right now — the scheduled run will retry automatically."
out ip ""; out created false
exit 0
