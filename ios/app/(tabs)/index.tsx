import { Pressable, StyleSheet } from "react-native";
import { Audio } from "expo-av";
import { Text, View, useThemeColor } from "@/components/Themed";
import { useEffect, useState } from "react";
import { IOSAudioQuality, IOSOutputFormat, Recording, RecordingStatus } from "expo-av/build/Audio";
import Colors from "@/constants/Colors";
import Animated, {
  useSharedValue,
  withTiming,
  useAnimatedStyle,
  Easing,
  withSequence,
  withDelay,
  cancelAnimation,
} from "react-native-reanimated";
import { Analysis } from "@/components/Analysis";
import FontAwesome from "@expo/vector-icons/FontAwesome";
import * as FileSystem from 'expo-file-system';



export default function TabOneScreen() {
  const [data, setData] = useState<any>();
  const backgroundColor = useThemeColor({}, "background");
  const textColor = useThemeColor({}, "text");
  const [recording, setRecording] = useState<Recording | undefined>();
  const [permissionResponse, requestPermission] = Audio.usePermissions();
  const [currentVolume, setCurrentVolume] = useState(0);

  const maxVolume = 100;
  const volume = useSharedValue(0);
  
  useEffect(() => {
    if (currentVolume === 0 || recording === undefined) {
      volume.value = 0;
      return;
    }
    if (currentVolume < -35) {
      return;
    }
    volume.value = withSequence(
      withTiming(1.05, {
        duration: 100,
        easing: Easing.linear,
      }),
      withDelay(200, withTiming(1, { duration: 100, easing: Easing.linear }))
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
          ios: {
            extension: '.m4a',
            outputFormat: IOSOutputFormat.MPEG4AAC,
            audioQuality: IOSAudioQuality.MAX,
            sampleRate: 44100,
            numberOfChannels: 2,
            bitRate: 128000,
            linearPCMBitDepth: 16,
            linearPCMIsBigEndian: false,
            linearPCMIsFloat: false,            
          }
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
    await recording?.stopAndUnloadAsync();
    await Audio.setAudioModeAsync({
      allowsRecordingIOS: false,
    });
    const uri = String(recording?.getURI());
  
    console.log(`Recording stored: ${uri}`);

    /*
      MAKE THE API CALL!!!!
    */

      const response = await fetch(uri);
      const response_ext = uri.split('.').pop()
      const blobData = await response.blob();
      const response_as_file = new File([blobData], "recording." + response_ext)
      const formData = new FormData();
      formData.append("file", response_as_file, 'recoring.m4a');
    console.log("FORM DATA IS " + JSON.stringify(formData))
    try {
      const response = await fetch(`${process.env.EXPO_PUBLIC_API_URL}upload/?user_id=3`, {
        method: 'POST',
        headers: {
          'Content-Type': 'multipart/form-data', // Use multipart/form-data for uploading files
          // Include additional headers if necessary
        },
        body: formData,
      });
  
      if (!response.ok) {
        throw new Error('Network response was not ok');
      }
  
      const body = await response.json();
      console.log("Response from server:", body);
      setData(body);
    } catch (error) {
      console.error('Error uploading file:', error);
    }
  
    setRecording(undefined);
  }

  if (data) {
    return (
      <View
        style={{
          position: "relative",
          width: "100%",
          paddingTop: 70,
          paddingHorizontal: 20,
        }}
      >
        <Pressable onPress={() => setData(undefined)}>
          <FontAwesome
            size={25}
            name="close"
            style={{ marginBottom: 10, color: "#dbdbdb" }}
          />
        </Pressable>
        <Analysis setData={setData} data={data} />
      </View>
    );
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
              backgroundColor: "#32a852",
              position: "absolute",
              opacity: 1,
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
    borderRadius: 30,
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
