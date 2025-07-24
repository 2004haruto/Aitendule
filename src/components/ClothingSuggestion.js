import React, { useEffect, useState } from "react";
import { View, Text, StyleSheet, Image, TextInput, TouchableOpacity, Alert } from "react-native";
import AsyncStorage from "@react-native-async-storage/async-storage";
import { ML_API_BASE_URL } from "@env";

export default function ClothingSuggestion() {
  const [suggestionText, setSuggestionText] = useState("読み込み中...");
  const [imageUrl, setImageUrl] = useState(null);
  const [recommendationItems, setRecommendationItems] = useState({});
  const [customizing, setCustomizing] = useState(false);
  const [customChoices, setCustomChoices] = useState({});
  const [isSaved, setIsSaved] = useState(false); // ✅ 追加

  useEffect(() => {
    const fetchSuggestion = async () => {
      try {
        const userId = await AsyncStorage.getItem("user_id");
        if (!userId) {
          setSuggestionText("ユーザーIDが見つかりません");
          return;
        }

        const res = await fetch(`${ML_API_BASE_URL}/api/v1/suggest`, {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ user_id: parseInt(userId) }),
        });

        if (!res.ok) throw new Error("APIリクエスト失敗");

        const data = await res.json();

        await AsyncStorage.setItem("temperature", String(data.temperature));
        await AsyncStorage.setItem("weather", data.weather || "");

        setSuggestionText(data.suggestion_text || "提案が取得できませんでした");
        setImageUrl(data.image_url || null);

        const categoryMap = {
          tops: "トップス",
          bottoms: "ボトムス",
          outer: "アウター",
          shoes: "靴",
          accessory: "小物",
        };

        const raw = data.recommendations || {};
        const mapped = Object.entries(raw).reduce((acc, [key, val]) => {
          acc[categoryMap[key] || key] = val;
          return acc;
        }, {});

        setRecommendationItems(mapped);
        setCustomChoices(mapped);
      } catch (error) {
        console.error("服装提案取得エラー:", error);
        setSuggestionText("服装提案の取得に失敗しました");
      }
    };

    fetchSuggestion();
  }, []);

  const handleSave = async (choiceItems, isRecommended) => {
    try {
      const userId = await AsyncStorage.getItem("user_id");
      const temperature = await AsyncStorage.getItem("temperature");
      const weather = await AsyncStorage.getItem("weather");

      await fetch(`${ML_API_BASE_URL}/api/v1/save_choice`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          user_id: parseInt(userId),
          choice: choiceItems,
          temperature: parseFloat(temperature),
          weather: weather,
          is_recommended: isRecommended
        }),
      });

      Alert.alert("保存しました", isRecommended ? "提案された服装を保存しました。" : "カスタム服装を保存しました。");
      setIsSaved(true); // ✅ 保存完了
      setCustomizing(false);
    } catch (error) {
      console.error("保存エラー:", error);
      Alert.alert("エラー", "保存に失敗しました。");
    }
  };

  return (
    <View style={styles.suggestionContainer}>
      <Text style={styles.sectionTitle}>AI服装提案</Text>

      <View style={styles.suggestionBox}>
        {imageUrl ? (
          <Image source={{ uri: imageUrl }} style={styles.suggestionImage} />
        ) : (
          <View style={styles.suggestionImagePlaceholder} />
        )}
        <View style={styles.suggestionTextContainer}>
          <Text style={styles.suggestionTitle}>今日のおすすめ</Text>
          <Text style={styles.suggestionDescription}>{suggestionText}</Text>
        </View>
      </View>

      {Object.keys(recommendationItems).length > 0 && (
        <View style={styles.recommendationList}>
          <Text style={styles.recommendationTitle}>👕 カテゴリー別アイテム</Text>
          {Object.entries(recommendationItems).map(([category, item]) => (
            <Text key={category} style={styles.recommendationItem}>
              {category}：{item}
            </Text>
          ))}
        </View>
      )}

      {!isSaved && !customizing && (
        <View style={{ flexDirection: 'row', marginTop: 16, justifyContent: 'space-around' }}>
          <TouchableOpacity style={styles.choiceButton} onPress={() => handleSave(recommendationItems, 1)}>
            <Text style={styles.choiceButtonText}>この服装を選ぶ</Text>
          </TouchableOpacity>
          <TouchableOpacity style={[styles.choiceButton, { backgroundColor: '#ccc' }]} onPress={() => setCustomizing(true)}>
            <Text style={styles.choiceButtonText}>違うものを選ぶ</Text>
          </TouchableOpacity>
        </View>
      )}

      {!isSaved && customizing && (
        <View style={{ marginTop: 16 }}>
          {Object.keys(recommendationItems).map((category) => (
            <View key={category} style={{ marginBottom: 8 }}>
              <Text style={{ fontSize: 12, marginBottom: 4 }}>{category}</Text>
              <TextInput
                value={customChoices[category] || ''}
                onChangeText={(text) => setCustomChoices((prev) => ({ ...prev, [category]: text }))}
                placeholder={`${category} を入力`}
                style={styles.input}
              />
            </View>
          ))}
          <TouchableOpacity style={[styles.choiceButton, { marginTop: 12 }]} onPress={() => handleSave(customChoices, 0)}>
            <Text style={styles.choiceButtonText}>この服装で登録する</Text>
          </TouchableOpacity>
        </View>
      )}
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
  suggestionImage: {
    width: 60,
    height: 60,
    borderRadius: 4,
    marginRight: 12,
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
    marginTop: 4,
  },
  recommendationList: {
    marginTop: 12,
  },
  recommendationTitle: {
    fontWeight: "bold",
    fontSize: 14,
    marginBottom: 4,
  },
  recommendationItem: {
    fontSize: 12,
    color: "#333",
  },
  choiceButton: {
    backgroundColor: '#007bff',
    padding: 10,
    borderRadius: 6,
  },
  choiceButtonText: {
    color: 'white',
    fontSize: 12,
    textAlign: 'center',
  },
  input: {
    borderColor: '#ccc',
    borderWidth: 1,
    borderRadius: 4,
    padding: 8,
    fontSize: 12,
  },
});
