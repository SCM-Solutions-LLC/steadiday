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

export const Safety: React.FC = () => {
  const frame = useCurrentFrame();

  return (
    <AbsoluteFill
      name="Safety scene"
      style={{
        display: "flex",
        flexDirection: "column",
        justifyContent: "center",
        alignItems: "center",
        backgroundColor: "#F8FAF9",
        gap: 56,
        paddingTop: 40,
      }}
    >
      <Interactive.Div
        name="Safety headline"
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
        Free safety essentials
      </Interactive.Div>
      <Interactive.Div
        name="Safety cards row"
        style={{
          display: "flex",
          flexDirection: "row",
          gap: 110,
          alignItems: "flex-start",
        }}
      >
        <Interactive.Div
          name="SOS card"
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
            name="SOS screenshot"
            src={staticFile("screenshot-05-sos.png")}
            style={{
              height: 600,
              borderRadius: 36,
              boxShadow: "0 16px 48px rgba(0, 0, 0, 0.14)",
            }}
          />
          <Interactive.Div
            name="SOS label"
            style={{
              fontFamily: sourceSans,
              fontWeight: 600,
              fontSize: 48,
              color: "#DC2626",
            }}
          >
            Emergency SOS
          </Interactive.Div>
        </Interactive.Div>
        <Interactive.Div
          name="Fall detection card"
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
            name="Fall detection screenshot"
            src={staticFile("screenshot-07-fall-detection.png")}
            style={{
              height: 600,
              borderRadius: 36,
              boxShadow: "0 16px 48px rgba(0, 0, 0, 0.14)",
            }}
          />
          <Interactive.Div
            name="Fall detection label"
            style={{
              fontFamily: sourceSans,
              fontWeight: 600,
              fontSize: 48,
              color: "#1F2937",
            }}
          >
            Fall Detection
          </Interactive.Div>
        </Interactive.Div>
        <Interactive.Div
          name="Medication card"
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
            name="Medication screenshot"
            src={staticFile("screenshot-02-medicines.png")}
            style={{
              height: 600,
              borderRadius: 36,
              boxShadow: "0 16px 48px rgba(0, 0, 0, 0.14)",
            }}
          />
          <Interactive.Div
            name="Medication label"
            style={{
              fontFamily: sourceSans,
              fontWeight: 600,
              fontSize: 48,
              color: "#4A9D7E",
            }}
          >
            Medication Reminders
          </Interactive.Div>
        </Interactive.Div>
      </Interactive.Div>
    </AbsoluteFill>
  );
};
