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

export const Wellness: React.FC = () => {
  const frame = useCurrentFrame();

  return (
    <AbsoluteFill
      name="Wellness scene"
      style={{
        display: "flex",
        flexDirection: "column",
        justifyContent: "center",
        alignItems: "center",
        backgroundColor: "#F0FAF5",
        gap: 56,
        paddingTop: 40,
      }}
    >
      <Interactive.Div
        name="Wellness headline"
        style={{
          fontFamily: poppins,
          fontWeight: 700,
          fontSize: 110,
          color: "#111827",
          opacity: interpolate(frame, [0, 15], [0, 1], {
            extrapolateLeft: "clamp",
            extrapolateRight: "clamp",
            easing: Easing.bezier(0.16, 1, 0.3, 1),
          }),
        }}
      >
        Wellness, made simple
      </Interactive.Div>
      <Interactive.Div
        name="Wellness cards row"
        style={{
          display: "flex",
          flexDirection: "row",
          gap: 110,
          alignItems: "flex-start",
        }}
      >
        <Interactive.Div
          name="Balance card"
          style={{
            display: "flex",
            flexDirection: "column",
            alignItems: "center",
            gap: 28,
            opacity: interpolate(frame, [10, 25], [0, 1], {
              extrapolateLeft: "clamp",
              extrapolateRight: "clamp",
              easing: Easing.bezier(0.16, 1, 0.3, 1),
            }),
            translate: interpolate(frame, [10, 25], ["0px 80px", "0px 0px"], {
              extrapolateLeft: "clamp",
              extrapolateRight: "clamp",
              easing: Easing.bezier(0.16, 1, 0.3, 1),
            }),
          }}
        >
          <Img
            name="Balance screenshot"
            src={staticFile("screenshot-04-steady-moves.png")}
            style={{
              height: 600,
              borderRadius: 36,
              boxShadow: "0 16px 48px rgba(0, 0, 0, 0.14)",
            }}
          />
          <Interactive.Div
            name="Balance label"
            style={{
              fontFamily: sourceSans,
              fontWeight: 600,
              fontSize: 48,
              color: "#1F2937",
            }}
          >
            Balance Exercises
          </Interactive.Div>
        </Interactive.Div>
        <Interactive.Div
          name="Family Link card"
          style={{
            display: "flex",
            flexDirection: "column",
            alignItems: "center",
            gap: 28,
            opacity: interpolate(frame, [20, 35], [0, 1], {
              extrapolateLeft: "clamp",
              extrapolateRight: "clamp",
              easing: Easing.bezier(0.16, 1, 0.3, 1),
            }),
            translate: interpolate(frame, [20, 35], ["0px 80px", "0px 0px"], {
              extrapolateLeft: "clamp",
              extrapolateRight: "clamp",
              easing: Easing.bezier(0.16, 1, 0.3, 1),
            }),
          }}
        >
          <Img
            name="Family Link screenshot"
            src={staticFile("screenshot-03-family-link.png")}
            style={{
              height: 600,
              borderRadius: 36,
              boxShadow: "0 16px 48px rgba(0, 0, 0, 0.14)",
            }}
          />
          <Interactive.Div
            name="Family Link label"
            style={{
              fontFamily: sourceSans,
              fontWeight: 600,
              fontSize: 48,
              color: "#5B8FC4",
            }}
          >
            Family Link Sharing
          </Interactive.Div>
        </Interactive.Div>
        <Interactive.Div
          name="Simple Mode card"
          style={{
            display: "flex",
            flexDirection: "column",
            alignItems: "center",
            gap: 28,
            opacity: interpolate(frame, [30, 45], [0, 1], {
              extrapolateLeft: "clamp",
              extrapolateRight: "clamp",
              easing: Easing.bezier(0.16, 1, 0.3, 1),
            }),
            translate: interpolate(frame, [30, 45], ["0px 80px", "0px 0px"], {
              extrapolateLeft: "clamp",
              extrapolateRight: "clamp",
              easing: Easing.bezier(0.16, 1, 0.3, 1),
            }),
          }}
        >
          <Img
            name="Simple Mode screenshot"
            src={staticFile("screenshot-01-simple-home.png")}
            style={{
              height: 600,
              borderRadius: 36,
              boxShadow: "0 16px 48px rgba(0, 0, 0, 0.14)",
            }}
          />
          <Interactive.Div
            name="Simple Mode label"
            style={{
              fontFamily: sourceSans,
              fontWeight: 600,
              fontSize: 48,
              color: "#4A9D7E",
            }}
          >
            Simple Mode
          </Interactive.Div>
        </Interactive.Div>
      </Interactive.Div>
    </AbsoluteFill>
  );
};
