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

export const Intro: React.FC = () => {
  const frame = useCurrentFrame();

  return (
    <AbsoluteFill
      name="Intro scene"
      style={{
        display: "flex",
        flexDirection: "column",
        justifyContent: "center",
        alignItems: "center",
        backgroundColor: "#FFFBF5",
        gap: 48,
      }}
    >
      <Img
        name="App icon"
        src={staticFile("icon.jpeg")}
        style={{
          width: 260,
          height: 260,
          borderRadius: 58,
          boxShadow: "0 24px 64px rgba(74, 157, 126, 0.35)",
          scale: interpolate(frame, [0, 25], [0, 1], {
            extrapolateLeft: "clamp",
            extrapolateRight: "clamp",
            easing: Easing.spring({ damping: 200 }),
            output: "perceptual-scale",
          }),
        }}
      />
      <Interactive.Div
        name="Brand name"
        style={{
          fontFamily: poppins,
          fontWeight: 700,
          fontSize: 150,
          color: "#4A9D7E",
          opacity: interpolate(frame, [15, 35], [0, 1], {
            extrapolateLeft: "clamp",
            extrapolateRight: "clamp",
            easing: Easing.bezier(0.16, 1, 0.3, 1),
          }),
          translate: interpolate(frame, [15, 35], ["0px 40px", "0px 0px"], {
            extrapolateLeft: "clamp",
            extrapolateRight: "clamp",
            easing: Easing.bezier(0.16, 1, 0.3, 1),
          }),
        }}
      >
        SteadiDay
      </Interactive.Div>
      <Interactive.Div
        name="Tagline"
        style={{
          fontFamily: sourceSans,
          fontWeight: 400,
          fontSize: 64,
          color: "#1F2937",
          opacity: interpolate(frame, [30, 50], [0, 1], {
            extrapolateLeft: "clamp",
            extrapolateRight: "clamp",
            easing: Easing.bezier(0.16, 1, 0.3, 1),
          }),
          translate: interpolate(frame, [30, 50], ["0px 40px", "0px 0px"], {
            extrapolateLeft: "clamp",
            extrapolateRight: "clamp",
            easing: Easing.bezier(0.16, 1, 0.3, 1),
          }),
        }}
      >
        Help, right when you need it.
      </Interactive.Div>
    </AbsoluteFill>
  );
};
