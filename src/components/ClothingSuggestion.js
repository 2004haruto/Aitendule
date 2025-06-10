import React, { useEffect, useState } from "react";
import { View, Text, StyleSheet } from "react-native";
import AsyncStorage from "@react-native-async-storage/async-storage";

export default function ClothingSuggestion() {
  const [suggestionText, setSuggestionText] = useState("読み込み中...");

  useEffect(() => {
    const fetchSuggestion = async () => {
      try {
        const userId = await AsyncStorage.getItem("user_id");

        if (!userId) {
          setSuggestionText("ユーザーIDが見つかりません");
          return;
        }

        const response = await fetch("http://10.104.0.167:3000/api/v1/suggest", {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
          },
          body: JSON.stringify({ user_id: parseInt(userId) }),
        });

        if (!response.ok) {
          throw new Error("APIリクエスト失敗");
        }

        const data = await response.json();
        setSuggestionText(data.recommendations || "提案がありませんでした");
      } catch (error) {
        console.error("服装提案取得エラー:", error);
        setSuggestionText("服装提案の取得に失敗しました");
      }
    };

    fetchSuggestion();
  }, []);

  return (
    <View style={styles.suggestionContainer}>
      <Text style={styles.sectionTitle}>AI服装提案</Text>
      <View style={styles.suggestionBox}>
        <View style={styles.suggestionImagePlaceholder} />
        <View style={styles.suggestionTextContainer}>
          <Text style={styles.suggestionTitle}>今日のおすすめ</Text>
          <Text style={styles.suggestionDescription}>{suggestionText}</Text>
        </View>
      </View>
    </View>
  );
}

const styles = StyleSheet.create({
  suggestionContainer: {
    backgroundColor: "white",
    padding: 16,
    borderRadius: 8,
    marginBottom: 16,
  },
  sectionTitle: {
    fontSize: 16,
    fontWeight: "bold",
    marginBottom: 12,
  },
  suggestionBox: {
    flexDirection: "row",
    alignItems: "center",
    backgroundColor: "#eee",
    padding: 12,
    borderRadius: 6,
  },
  suggestionImagePlaceholder: {
    width: 60,
    height: 60,
    backgroundColor: "#ddd",
    marginRight: 12,
    borderRadius: 4,
  },
  suggestionTextContainer: {
    flex: 1,
  },
  suggestionTitle: {
    fontWeight: "bold",
    fontSize: 14,
  },
  suggestionDescription: {
    color: "gray",
    fontSize: 12,
  },
});
