import { defineConfig, Options } from "tsup";

export default defineConfig((options: Options) => ({
  entry: ["src/index.ts"],
  clean: true,
  format: ["cjs", "esm"],
  treeshake: true,
  dts: true,
  ...options,
}));
