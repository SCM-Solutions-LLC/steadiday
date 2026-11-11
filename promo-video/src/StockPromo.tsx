import { poppins, sourceSans } from "./fonts";
import {
  AbsoluteFill,
  Audio,
  Easing,
  Img,
  interpolate,
  OffthreadVideo,
  Sequence,
  staticFile,
  useCurrentFrame,
} from "remotion";

const GREEN = "#4A9D7E";
const FPS = 30;

// clip: file in public/stock/ once downloaded from Pexels; null renders a labelled placeholder.
type Beat = {
  sec: number;
  query: string;
  clip: string | null;
  start?: number; // seconds into the clip
  shot?: string;
  caption: string;
  vo: [number, number]; // seconds into public/vo.mp3 for this beat's line
};

export const BEATS: Beat[] = [
  { sec: 5, query: "senior woman walking stairs", clip: "beat4.mp4", caption: "Mom lives alone.\nYou live three hours away.", vo: [0, 3.14] },
  { sec: 5, query: "man looking at phone smiling", clip: "beat2.mp4", caption: "You can't be there\nevery day.\nBut you can stay close.", vo: [3.14, 6.76] },
  { sec: 7, query: "senior climbing stairs home", clip: "beat1.mp4", shot: "screenshot-07-fall-detection.png", caption: "If SteadiDay senses a fall,\nit can alert family.", vo: [6.76, 9.97] },
  { sec: 6, query: "senior kitchen morning", clip: "beat4.mp4", start: 12, shot: "screenshot-02-medicines.png", caption: "The right medicine,\non time.", vo: [9.97, 12.2] },
  { sec: 8, query: "grandmother phone video chat", clip: "beat5.mp4", shot: "screenshot-05-sos.png", caption: "One tap sends an SOS.\nShare how her day\nis going.", vo: [12.2, 15.94] },
  { sec: 7, query: "senior balance exercise", clip: "beat6.mp4", shot: "screenshot-04-steady-moves.png", caption: "Gentle balance exercises,\nevery day.", vo: [15.94, 18.81] },
];
const END_SEC = 7;
export const STOCK_PROMO_FRAMES =
  (BEATS.reduce((s, b) => s + b.sec, 0) + END_SEC) * FPS;

const END_VO: [number, number] = [18.81, 22.05];

// One VO take, cut at the pauses between lines, so each line starts with its beat.
const VoLine: React.FC<{ vo: [number, number] }> = ({ vo }) => (
  <Sequence from={10} layout="none">
    <Audio
      src={staticFile("vo.mp3")}
      trimBefore={Math.round(vo[0] * FPS)}
      trimAfter={Math.round(vo[1] * FPS)}
    />
  </Sequence>
);

const ease = (frame: number, start: number, end: number) =>
  interpolate(frame, [start, end], [0, 1], {
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
    easing: Easing.bezier(0.16, 1, 0.3, 1),
  });

const BeatScene: React.FC<{ beat: Beat; frames: number }> = ({ beat, frames }) => {
  const frame = useCurrentFrame();
  const shotIn = ease(frame, 6, 16);
  const capIn = ease(frame, 0, 8);
  return (
    <AbsoluteFill style={{ backgroundColor: "#111111" }}>
      {beat.clip ? (
        <OffthreadVideo
          src={staticFile(`stock/${beat.clip}`)}
          muted
          trimBefore={(beat.start ?? 0) * FPS}
          style={{ width: "100%", height: "100%", objectFit: "cover" }}
        />
      ) : (
        <AbsoluteFill
          style={{
            background: "radial-gradient(circle at 50% 35%, #2B4A3F, #111111 70%)",
            justifyContent: "flex-start",
            alignItems: "center",
            paddingTop: 80,
            fontFamily: sourceSans,
            fontSize: 36,
            color: "#7FA899",
          }}
        >
          stock: {beat.query}
        </AbsoluteFill>
      )}
      {/* scrim keeps captions readable over any footage */}
      <AbsoluteFill
        style={{
          background:
            "linear-gradient(to bottom, rgba(0,0,0,0) 45%, rgba(0,0,0,0.75) 100%)",
        }}
      />
      {beat.shot ? (
        <AbsoluteFill style={{ alignItems: "center", paddingTop: 220 }}>
          <Img
            src={staticFile(beat.shot)}
            style={{
              height: 1050,
              borderRadius: 48,
              border: "6px solid #FFFFFF",
              boxShadow: "0 24px 64px rgba(0,0,0,0.45)",
              opacity: shotIn,
              translate: `0px ${(1 - shotIn) * 120}px`,
              scale: String(interpolate(frame, [0, frames], [1, 1.04])),
            }}
          />
        </AbsoluteFill>
      ) : null}
      <AbsoluteFill
        style={{
          justifyContent: "flex-end",
          alignItems: "center",
          paddingBottom: 220,
          paddingLeft: 64,
          paddingRight: 64,
        }}
      >
        <div
          style={{
            fontFamily: poppins,
            fontWeight: 700,
            fontSize: 68,
            lineHeight: 1.2,
            color: "#FFFFFF",
            textAlign: "center",
            whiteSpace: "pre-line",
            textShadow: "0 4px 16px rgba(0,0,0,0.6)",
            opacity: capIn,
            translate: `0px ${(1 - capIn) * 30}px`,
          }}
        >
          {beat.caption}
        </div>
      </AbsoluteFill>
    </AbsoluteFill>
  );
};

const EndCard: React.FC = () => {
  const frame = useCurrentFrame();
  return (
    <AbsoluteFill
      style={{
        backgroundColor: GREEN,
        justifyContent: "center",
        alignItems: "center",
        gap: 56,
      }}
    >
      <Img
        src={staticFile("icon.jpeg")}
        style={{ width: 260, borderRadius: 60, opacity: ease(frame, 0, 12) }}
      />
      <div
        style={{
          fontFamily: poppins,
          fontWeight: 700,
          fontSize: 110,
          color: "#FFFFFF",
          opacity: ease(frame, 6, 18),
        }}
      >
        SteadiDay
      </div>
      <div
        style={{
          fontFamily: sourceSans,
          fontWeight: 600,
          fontSize: 60,
          color: "#F0FAF5",
          opacity: ease(frame, 14, 26),
        }}
      >
        Peace of mind, every day.
      </div>
      <Img
        src={staticFile("app-store-badge.svg")}
        style={{ width: 480, opacity: ease(frame, 24, 36) }}
      />
      <div
        style={{
          fontFamily: sourceSans,
          fontWeight: 600,
          fontSize: 52,
          color: "#FFFFFF",
          opacity: ease(frame, 32, 44),
        }}
      >
        or visit www.steadiday.com
      </div>
    </AbsoluteFill>
  );
};

export const StockPromo: React.FC = () => {
  let from = 0;
  return (
    <AbsoluteFill style={{ backgroundColor: "#111111" }}>
      {BEATS.map((beat) => {
        const frames = beat.sec * FPS;
        const seq = (
          <Sequence key={beat.query} from={from} durationInFrames={frames}>
            <BeatScene beat={beat} frames={frames} />
            <VoLine vo={beat.vo} />
          </Sequence>
        );
        from += frames;
        return seq;
      })}
      <Sequence from={from} durationInFrames={END_SEC * FPS}>
        <EndCard />
        <VoLine vo={END_VO} />
      </Sequence>
    </AbsoluteFill>
  );
};
