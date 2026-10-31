// Runs on every container start (docker-entrypoint.sh): seeds the store once, then makes sure the
// admin account from ADMIN_EMAIL / ADMIN_PASSWORD exists. Safe to run repeatedly.
import { ExecArgs } from "@medusajs/framework/types";
import { ContainerRegistrationKeys, Modules } from "@medusajs/framework/utils";
import { createUserAccountWorkflow } from "@medusajs/medusa/core-flows";
import seedJrly from "./seed";

export default async function bootstrap(args: ExecArgs) {
  const { container } = args;
  const logger = container.resolve(ContainerRegistrationKeys.LOGGER);
  await seedJrly(args);

  const email = process.env.ADMIN_EMAIL?.trim().toLowerCase();
  const password = process.env.ADMIN_PASSWORD;
  if (!email || !password) {
    logger.info("ADMIN_EMAIL / ADMIN_PASSWORD not set, skipping admin account.");
    return;
  }
  if (password.length < 12) throw new Error("ADMIN_PASSWORD must be at least 12 characters");

  const users = container.resolve(Modules.USER);
  const [existing] = await users.listUsers({ email });
  if (existing) {
    logger.info(`Admin ${email} already exists.`);
    return;
  }
  const auth = container.resolve(Modules.AUTH);
  const { authIdentity, error } = await auth.register("emailpass", { body: { email, password } } as never);
  if (error || !authIdentity) throw new Error(`Could not register admin: ${error ?? "unknown error"}`);
  await createUserAccountWorkflow(container).run({ input: { authIdentityId: authIdentity.id, userData: { email } } });
  logger.info(`Admin ${email} created. Log in at /app`);
}
