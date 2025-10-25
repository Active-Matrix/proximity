import { defineConfig, Options } from "tsup";
import { resolve } from "path";

export default defineConfig((options: Options) => ({
  entry: ["src/index.ts"],
  clean: true,
  format: ["cjs", "esm"],
  treeshake: true,
  dts: true,
  esbuildOptions: (esbuildOptions) => {
    // Ensure esbuildOptions resolves alias for '@'
    esbuildOptions.alias = {
      "@": resolve(__dirname, "./"),
    };
  },
  ...options,
}));
