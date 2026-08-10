import "./index.css";
import { Composition, Folder } from "remotion";
import { PromoVideo } from "./PromoVideo";
import { CallToAction } from "./scenes/CallToAction";
import { Intro } from "./scenes/Intro";
import { Safety } from "./scenes/Safety";
import { Wellness } from "./scenes/Wellness";

export const RemotionRoot: React.FC = () => {
  return (
    <>
      <Composition
        id="SteadiDayPromo"
        component={PromoVideo}
        durationInFrames={615}
        fps={30}
        width={1920}
        height={1080}
      />
      <Folder name="SteadiDayPromo-Scenes">
        <Composition
          id="Intro"
          component={Intro}
          durationInFrames={150}
          fps={30}
          width={1920}
          height={1080}
        />
        <Composition
          id="Safety"
          component={Safety}
          durationInFrames={180}
          fps={30}
          width={1920}
          height={1080}
        />
        <Composition
          id="Wellness"
          component={Wellness}
          durationInFrames={180}
          fps={30}
          width={1920}
          height={1080}
        />
        <Composition
          id="CallToAction"
          component={CallToAction}
          durationInFrames={150}
          fps={30}
          width={1920}
          height={1080}
        />
      </Folder>
    </>
  );
};
