import { poppins, sourceSans } from "../fonts";
import {
  AbsoluteFill,
  Easing,
  Img,
  Interactive,
  interpolate,
  staticFile,
  useCurrentFrame,
} from "remotion";

export const CallToAction: React.FC = () => {
  const frame = useCurrentFrame();

  return (
    <AbsoluteFill
      name="Call to action scene"
      style={{
        display: "flex",
        flexDirection: "column",
        justifyContent: "center",
        alignItems: "center",
        backgroundColor: "#4A9D7E",
        gap: 56,
      }}
    >
      <Interactive.Div
        name="CTA headline"
        style={{
          fontFamily: poppins,
          fontWeight: 700,
          fontSize: 130,
          color: "#FFFFFF",
          textAlign: "center",
          opacity: interpolate(frame, [0, 18], [0, 1], {
            extrapolateLeft: "clamp",
            extrapolateRight: "clamp",
            easing: Easing.bezier(0.16, 1, 0.3, 1),
          }),
          translate: interpolate(frame, [0, 18], ["0px 50px", "0px 0px"], {
            extrapolateLeft: "clamp",
            extrapolateRight: "clamp",
            easing: Easing.bezier(0.16, 1, 0.3, 1),
          }),
        }}
      >
        Peace of mind, free.
      </Interactive.Div>
      <Interactive.Div
        name="CTA subline"
        style={{
          fontFamily: sourceSans,
          fontWeight: 400,
          fontSize: 60,
          color: "#F0FAF5",
          opacity: interpolate(frame, [12, 30], [0, 1], {
            extrapolateLeft: "clamp",
            extrapolateRight: "clamp",
            easing: Easing.bezier(0.16, 1, 0.3, 1),
          }),
        }}
      >
        Designed for adults 50+ and the families who love them.
      </Interactive.Div>
      <Img
        name="App Store badge"
        src={staticFile("app-store-badge.svg")}
        style={{
          width: 480,
          scale: interpolate(frame, [25, 45], [0, 1], {
            extrapolateLeft: "clamp",
            extrapolateRight: "clamp",
            easing: Easing.spring({ damping: 200 }),
            output: "perceptual-scale",
          }),
        }}
      />
      <Interactive.Div
        name="Website URL"
        style={{
          fontFamily: sourceSans,
          fontWeight: 600,
          fontSize: 52,
          color: "#FFFFFF",
          opacity: interpolate(frame, [40, 58], [0, 1], {
            extrapolateLeft: "clamp",
            extrapolateRight: "clamp",
            easing: Easing.bezier(0.16, 1, 0.3, 1),
          }),
        }}
      >
        steadiday.com
      </Interactive.Div>
    </AbsoluteFill>
  );
};
