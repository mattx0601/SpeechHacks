import { StyleSheet, TouchableOpacity, useColorScheme } from "react-native";
import { HeaderText } from "./StyledText";
import { Text, View } from "./Themed";
import Colors from "@/constants/Colors";
import { useState } from "react";

export function Analysis({
  setData,
  data,
}: {
  setData: (data: any) => void;
  data: any;
}) {
  const [progress, setProgress] = useState(1);
  const colorScheme = useColorScheme() ?? "light";
  const increment = () => {
    if (progress === data.count) {
      setProgress(data.count);
      setData(undefined);
      return;
    }

    setProgress((curr) => (curr += 1));
  };

  return (
    <View style={{ paddingTop: 10 }}>
      <View style={{ marginBottom: 30 }}>
        <View style={{ position: "relative" }}>
          <View
            style={[
              styles.progress,
              { borderWidth: 1, borderColor: Colors.dark.text, opacity: 0.2 },
            ]}
          />
          <View
            style={[
              styles.progress,
              {
                backgroundColor: "#32a852",
                width: `${(progress / data.count) * 100}%`,
                marginBottom: 0,
                position: "absolute",
                top: 0,
                left: 0,
                height: 15,
                borderTopRightRadius: progress === data.count ? 30 : 0,
                borderBottomRightRadius: progress === data.count ? 30 : 0,
              },
            ]}
          />
        </View>
      </View>
      <View style={{ rowGap: 20, height: "80%" }}>
        <View>
          <HeaderText
            style={{
              fontSize: 24,
              marginBottom: 10,
            }}
          >
            Transcription
          </HeaderText>
          <Text>"{data.originaltext}"</Text>
        </View>
        <View
          style={{
            flex: 1,
            flexDirection: "row",
          }}
        >
          <View>
            <HeaderText
              style={{
                fontSize: 18,
                marginBottom: 10,
              }}
            >
              Instead of
            </HeaderText>
            <Text
              style={{
                backgroundColor: `${Colors[colorScheme].text}20`,
                padding: 10,
                marginRight: 30,
              }}
            >
              "{data[`${progress}`].original}"
            </Text>
          </View>
          <View style={{ width: "auto" }}>
            <HeaderText style={{ fontSize: 18, marginBottom: 10 }}>
              Say
            </HeaderText>
            <Text
              style={{
                backgroundColor: `${Colors[colorScheme].text}20`,
                padding: 10,
              }}
            >
              "{data[`${progress}`].corrected}""
            </Text>
          </View>
        </View>
      </View>
      <TouchableOpacity
        activeOpacity={0.9}
        onPress={increment}
        style={{
          backgroundColor: progress === data.count ? "#32a852" : "#dbdbdb",
          height: 50,
          width: "100%",
          borderRadius: 30,
          alignItems: "center",
          justifyContent: "center",
          position: "absolute",
          bottom: 0,
        }}
      >
        <HeaderText
          style={{
            fontSize: 15,
            color:
              progress === data.count
                ? Colors["dark"].text
                : colorScheme === "light"
                ? Colors[colorScheme].text
                : Colors[colorScheme].background,
          }}
        >
          {progress === data.count ? "Done" : "Continue"}
        </HeaderText>
      </TouchableOpacity>
    </View>
  );
}

const styles = StyleSheet.create({
  progress: {
    height: 15,
    backgroundColor: "transparent",
    borderRadius: 30,
    marginBottom: 20,
    width: "100%",
  },
});
