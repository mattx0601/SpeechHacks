import { Text, View } from "./Themed";

export function Chat({ data }: { data: any }) {
  return (
    <View
      style={{
        width: "100%",
        alignContent: data.agent === "ai" ? "flex-start" : "flex-end",
      }}
    >
      <Text>{data.message}</Text>
    </View>
  );
}
