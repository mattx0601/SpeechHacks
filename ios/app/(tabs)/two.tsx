import { Animated, StyleSheet, useColorScheme } from "react-native";

import EditScreenInfo from "@/components/EditScreenInfo";
import { Text, View } from "@/components/Themed";
import { useEffect, useRef, useState } from "react";
import { Chat } from "@/components/chat";

const FAKE_DATA = [
  {
    agent: "ai",
    message: "Hi how can I help you today?",
  },
  {
    agent: "user",
    message: "Hello!",
  },
];

export default function TabTwoScreen() {
  const [loaded, setLoaded] = useState(false);
  const colorScheme = useColorScheme() ?? "light";
  const [chats, setChats] = useState(FAKE_DATA);
  /*
    The data should look something like this:
    [
      {
        "agent": "ai",
        "message": "Hi how can i help you"
      },
      {
        "agent": "user",
        "message": "I'm in love with friend, what should I do?"
      }
    ]

    From here, you can simply map the components in the HTML
    {chats.map((c) => (
      <Chat data={c} />
    ))}

  */

  const loadingRef = useRef(new Animated.Value(0)).current;

  useEffect(() => {
    Animated.timing(loadingRef, {
      toValue: 360,
      duration: 1000,
      useNativeDriver: true,
    });

    const userId = Math.floor(Math.random() * 100000); //Terrible way to generate a id btw. lol
    const res = fetch(
      `${process.env.EXPO_PUBLIC_API_URL}/conv_starter/${userId}`,
      {
        method: "GET",
      }
    )
      .then(async (r) => {
        const body = await r.json();
        /*
          This is the initial message. Append it to the data
          const { message } = body;
          const newState = [...chats, message]
          setChats(newState);
        */
        setLoaded(true);
      })
      .catch((e) => {
        console.log(e);
        setLoaded(true);
      });
  }, []);

  if (!loaded) {
    return (
      <Animated.View
        style={{
          flex: 1,
          alignItems: "center",
          justifyContent: "center",
          transform: [
            {
              rotateZ: loadingRef.interpolate({
                inputRange: [0, 360],
                outputRange: ["0deg", "360deg"],
              }),
            },
          ],
        }}
      >
        <Text>Loading</Text>
      </Animated.View>
    );
  }

  return (
    <View
      style={[
        styles.container,
        {
          paddingTop: 70,
          paddingHorizontal: 20,
          rowGap: 10,
        },
      ]}
    >
      {chats.map((c) => (
        <Chat key={c.message} data={c} />
      ))}
    </View>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
  },
  title: {
    fontSize: 20,
    fontWeight: "bold",
  },
  separator: {
    marginVertical: 30,
    height: 1,
    width: "80%",
  },
});
