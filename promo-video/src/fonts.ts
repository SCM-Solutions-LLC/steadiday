import { loadFont } from "@remotion/fonts";
import { staticFile } from "remotion";

export const poppins = "Poppins";
export const sourceSans = "Source Sans 3";

await Promise.all([
  loadFont({
    family: poppins,
    url: staticFile("fonts/Poppins-SemiBold.woff2"),
    weight: "600",
  }),
  loadFont({
    family: poppins,
    url: staticFile("fonts/Poppins-Bold.woff2"),
    weight: "700",
  }),
  loadFont({
    family: sourceSans,
    url: staticFile("fonts/SourceSans3.woff2"),
    weight: "400",
  }),
  loadFont({
    family: sourceSans,
    url: staticFile("fonts/SourceSans3.woff2"),
    weight: "600",
  }),
]);
