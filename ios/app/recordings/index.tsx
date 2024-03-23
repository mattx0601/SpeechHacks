import { Text, View } from "@/components/Themed";
import { StyleSheet } from "react-native";
export default function Page() {
  return (
    <View style={styles.container}>
      <Text
        style={{
          fontFamily: "Inter",
          fontSize: 18,
          fontWeight: "bold",
        }}
      >
        Hi
      </Text>
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
});
