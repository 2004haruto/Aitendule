import React from "react";
import { View, Text, StyleSheet } from "react-native";

export default function ClothingSuggestion({ suggestionText }) {
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
