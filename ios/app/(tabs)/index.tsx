import { Pressable, StyleSheet } from "react-native";
import { Audio } from "expo-av";
import EditScreenInfo from "@/components/EditScreenInfo";
import { Text, View, useThemeColor } from "@/components/Themed";
import { useState } from "react";
import { Recording } from "expo-av/build/Audio";
import { useColorScheme } from "@/components/useColorScheme.web";
import Colors from "@/constants/Colors";

export default function TabOneScreen() {
  const backgroundColor = useThemeColor({}, "background");
  const textColor = useThemeColor({}, "text");
  const [recording, setRecording] = useState<Recording | undefined>();
  const [permissionResponse, requestPermission] = Audio.usePermissions();

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
        Audio.RecordingOptionsPresets.HIGH_QUALITY
      );
      setRecording(recording);
      console.log("Recording started");
    } catch (err) {
      console.error("Failed to start recording", err);
    }
  }

  async function stopRecording() {
    console.log("Stopping recording");
    const uri = recording?.getURI(); //this is what we use to send our api call
    setRecording(undefined);
    await recording?.stopAndUnloadAsync();
    await Audio.setAudioModeAsync({
      allowsRecordingIOS: false,
    });
    console.log(`Recording stored: ${uri}`);
  }

  return (
    <View style={{ ...styles.container, backgroundColor }}>
      <Pressable
        onPress={recording ? stopRecording : startRecording}
        style={{
          ...styles.button,
          backgroundColor: recording ? "#d13f3f" : "#dbdbdb",
        }}
      >
        <Text style={{ ...styles.title, color: Colors.light.text }}>
          {recording ? "Recording" : "Tap to record"}
        </Text>
      </Pressable>
    </View>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    alignItems: "center",
    justifyContent: "center",
  },
  button: {
    borderRadius: 100,
    width: 150,
    height: 150,
    alignItems: "center",
    justifyContent: "center",
  },
  title: {
    fontSize: 15,
    fontWeight: "bold",
  },
});
