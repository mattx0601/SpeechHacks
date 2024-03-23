import { Pressable, StyleSheet } from "react-native";
import { Audio } from "expo-av";
import { Text, View, useThemeColor } from "@/components/Themed";
import { useEffect, useState } from "react";
import { Recording, RecordingStatus } from "expo-av/build/Audio";
import Colors from "@/constants/Colors";
import Animated, {
  useSharedValue,
  withTiming,
  useAnimatedStyle,
  Easing,
  withRepeat,
  withSequence,
  withDelay,
  cancelAnimation,
} from "react-native-reanimated";
import { router } from "expo-router";

export default function TabOneScreen() {
  const backgroundColor = useThemeColor({}, "background");
  const textColor = useThemeColor({}, "text");
  const [recording, setRecording] = useState<Recording | undefined>();
  const [permissionResponse, requestPermission] = Audio.usePermissions();
  const [currentVolume, setCurrentVolume] = useState(0);

  const maxVolume = 100;
  const volume = useSharedValue(0);

  useEffect(() => {
    cancelAnimation(volume);
    if (currentVolume === 0 || recording === undefined) {
      volume.value = 0;
      return;
    }
    volume.value = withSequence(
      withTiming(Math.abs((currentVolume + 50) / maxVolume) + 1, {
        duration: 100,
        easing: Easing.linear,
      }),
      withDelay(100, withTiming(1, { duration: 100, easing: Easing.linear }))
    );
  }, [currentVolume]);

  async function updateStatus(status: RecordingStatus) {
    const metering = status.metering;
    setCurrentVolume(metering ?? 0);
  }

  const volumeStyle = useAnimatedStyle(() => ({
    transform: [{ scale: volume.value }],
  }));

  async function startRecording() {
    try {
      if (permissionResponse?.status !== "granted") {
        console.log("Requesting permission");
        await requestPermission();
      }
      await Audio.setAudioModeAsync({
        allowsRecordingIOS: true,
        playsInSilentModeIOS: true,
      });

      console.log("Starting recording");
      const { recording } = await Audio.Recording.createAsync(
        {
          ...Audio.RecordingOptionsPresets.HIGH_QUALITY,
          isMeteringEnabled: true,
        },
        updateStatus
      );
      setRecording(recording);
      console.log("Recording started");
    } catch (err) {
      console.error("Failed to start recording", err);
    }
  }

  async function stopRecording() {
    console.log("Stopping recording");
    const uri = recording?.getURI(); //this is the audio file we use to send our api call
    setRecording(undefined);
    await recording?.stopAndUnloadAsync();
    await Audio.setAudioModeAsync({
      allowsRecordingIOS: false,
    });
    console.log(`Recording stored: ${uri}`);

    router.push("/recordings/");
  }

  return (
    <View style={{ ...styles.container, backgroundColor }}>
      <Pressable
        onPress={recording ? stopRecording : startRecording}
        style={{
          ...styles.button,
          backgroundColor: recording ? "#d13f3f" : "#dbdbdb",
          zIndex: 10,
        }}
      >
        <Text style={{ ...styles.title, color: Colors.light.text }}>
          {recording ? "Recording" : "Tap to record"}
        </Text>
      </Pressable>
      {recording && (
        <Animated.View
          style={[
            styles.button,
            {
              backgroundColor: "#dbdbdb",
              position: "absolute",
              opacity: 0.2,
            },
            volumeStyle,
          ]}
        />
      )}
    </View>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    alignItems: "center",
    justifyContent: "center",
    position: "relative",
  },
  button: {
    borderRadius: 10,
    width: 150,
    height: 80,
    alignItems: "center",
    justifyContent: "center",
  },
  title: {
    fontSize: 16,
    fontWeight: "bold",
    fontFamily: "CalSans",
  },
});
