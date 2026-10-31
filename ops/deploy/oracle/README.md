# Medusa on Oracle Cloud Always Free — phone-only setup

**Cost:** ₱0. Oracle asks for a card to verify identity and puts a small temporary hold on it. Always Free resources are not charged.
**Result:** Medusa admin and API live at `https://<your-ip>.sslip.io` with free HTTPS, always on, and 48 products already loaded.
**Time:** about 20 minutes of tapping, then about 10 minutes of waiting.

Everything below works in a phone browser. Desktop mode helps on some Oracle screens.

## 1. Create the account
1. Go to <https://signup.cloud.oracle.com>.
2. **Home region: Singapore or Japan East.** These are close to the Philippines. The region can't be changed later.
3. Verify your email and card.

## 2. Create the server
1. Open Menu → **Compute → Instances → Create instance**.
2. **Image:** Canonical Ubuntu 24.04. **Shape:** Ampere → **VM.Standard.A1.Flex**, 2 OCPU, 12 GB.
   - If you see "Out of capacity": try another Availability Domain, or 1 OCPU / 6 GB.
3. **Networking:** keep the defaults and make sure **Assign a public IPv4 address** is on.
4. **SSH keys:** choose **Generate a key pair** and save the private key to your phone or Drive. You only need it for repairs.
5. Open **Show advanced options → Management → Initialization script → Paste cloud-init script** and paste the script below, after changing the email and password:

```bash
#!/bin/bash
export ADMIN_EMAIL='you@example.com'
export ADMIN_PASSWORD='ChangeMe-Strong-Password-123'
curl -fsSL https://raw.githubusercontent.com/johnyumang/REPO-JRLY.portfolio/main/ops/deploy/oracle/install.sh | bash
```

   Password rule: at least 12 characters, using letters, numbers and `-`. **Do not use `$`, quotes or spaces.**

6. Tap **Create**. Copy the **Public IP address** shown on the instance page.

## 3. Open the web ports
1. On the instance page, open **Subnet → Default Security List → Add Ingress Rules**.
2. Source CIDR `0.0.0.0/0`, IP protocol TCP, destination port **80**. Add.
3. Repeat with destination port **443**.

## 4. Open your admin
Wait about 10 minutes for the first build, then open:

- Admin: `https://<IP-with-dashes>.sslip.io/app`. For example, IP `140.238.1.2` becomes `https://140-238-1-2.sslip.io/app`.
- Log in with the email and password from step 2.5. The installer erases the password from the server once the admin user exists.

Then tell Claude the address. Claude adds it to the status board, so you can see up/down at a glance.

## Repairs (Oracle Cloud Shell, the `>_` icon at the top of the console)
```bash
ssh -i <your-key> ubuntu@<IP>
sudo docker compose -f /opt/jrly/docker-compose.yml logs --tail 100 medusa   # see errors
sudo bash -c "$(curl -fsSL https://raw.githubusercontent.com/johnyumang/REPO-JRLY.portfolio/main/ops/deploy/oracle/install.sh)"   # update / restart, keeps data
```

## What's inside
| File | Purpose |
|---|---|
| `install.sh` | Installs Docker, opens the firewall, fetches code, writes secrets to `/opt/jrly/.env` (root only), builds, starts and waits for health |
| `docker-compose.yml` | Postgres 16, Redis 7, Medusa, and Caddy for automatic HTTPS |
| `Dockerfile` | Builds Medusa. Works on ARM (Oracle) and x86 |
| `entrypoint.sh` | Every start: migrate. First start only: seed 48 products and create the admin |

**Tested 2026-10-31 in Docker:** build passes, migrations run, the 48-product seed runs, admin login returns 200, the admin app returns 200, and a restart does not re-seed.
**Not tested yet:** a real Oracle VM and Caddy HTTPS (these need the live server).

**Watch out:** Oracle can reclaim Always Free VMs that sit almost idle for 7 days. The hourly status-board check gives the server a little traffic, but keep an eye on it.
