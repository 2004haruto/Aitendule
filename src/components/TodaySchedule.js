import React, { useState, useEffect } from "react";
import {
  View,
  Text,
  TouchableOpacity,
  ActivityIndicator,
  Alert,
  ScrollView,
} from "react-native";
import * as Calendar from "expo-calendar";

export default function TodaySchedule() {
  const [events, setEvents] = useState([]);
  const [loading, setLoading] = useState(false);
  const [permissionGranted, setPermissionGranted] = useState(false);
  const [calendarColorMap, setCalendarColorMap] = useState({});

  useEffect(() => {
    requestCalendarPermission();
  }, []);

  const requestCalendarPermission = async () => {
    try {
      const { status } = await Calendar.requestCalendarPermissionsAsync();
      if (status === "granted") {
        setPermissionGranted(true);
        fetchTodayEvents();
      } else {
        Alert.alert("カレンダーアクセスが拒否されました");
      }
    } catch (error) {
      console.error("パーミッションエラー:", error);
      Alert.alert("カレンダーへのアクセス中にエラーが発生しました");
    }
  };

  const fetchTodayEvents = async () => {
    setLoading(true);
    try {
      const calendars = await Calendar.getCalendarsAsync();
      const calendarIds = calendars.map((cal) => cal.id);

      // カレンダーの色をマップ
      const colorMap = {};
      calendars.forEach((cal) => {
        colorMap[cal.id] = cal.color || "gray";
      });
      setCalendarColorMap(colorMap);

      const startOfDay = new Date();
      startOfDay.setHours(0, 0, 0, 0);

      const endOfDay = new Date();
      endOfDay.setHours(23, 59, 59, 999);

      const allEvents = [];

      for (const calendarId of calendarIds) {
        const events = await Calendar.getEventsAsync(
          [calendarId],
          startOfDay,
          endOfDay
        );
        allEvents.push(...events);
      }

      // 重複削除
      const uniqueEvents = Array.from(
        new Map(
          allEvents.map((e) => [`${e.id}-${e.startDate}`, e])
        ).values()
      );

      uniqueEvents.sort((a, b) => new Date(a.startDate) - new Date(b.startDate));
      setEvents(uniqueEvents);
    } catch (error) {
      console.error("イベント取得エラー:", error);
      Alert.alert("カレンダーの予定取得中にエラーが発生しました");
    } finally {
      setLoading(false);
    }
  };

  const formatEventTime = (event) => {
    if (event.allDay) return "終日";

    const start = new Date(event.startDate);
    const end = new Date(event.endDate);

    const format = { hour: "2-digit", minute: "2-digit" };
    const startStr = start.toLocaleTimeString([], format);
    const endStr = end.toLocaleTimeString([], format);

    return `${startStr} ~ ${endStr}`;
  };

  return (
    <ScrollView contentContainerStyle={{ padding: 16 }}>
      <Text style={{ fontSize: 20, fontWeight: "bold", marginBottom: 16 }}>
        今日の予定
      </Text>

      {!permissionGranted ? (
        <Text style={{ color: "gray" }}>カレンダーのアクセス許可が必要です。</Text>
      ) : loading ? (
        <ActivityIndicator size="large" color="#0000ff" />
      ) : events.length === 0 ? (
        <Text style={{ color: "gray" }}>本日の予定はありません。</Text>
      ) : (
        events.map((event) => {
          const calendarColor = calendarColorMap[event.calendarId] || "gray";
          const timeStr = formatEventTime(event);

          return (
            <View
              key={`${event.id}-${event.startDate}`}
              style={{
                flexDirection: "row",
                alignItems: "center",
                marginBottom: 12,
                paddingLeft: 8,
                borderLeftWidth: 4,
                borderLeftColor: calendarColor,
              }}
            >
              {/* アイコンは表示しない */}
              <View>
                <Text style={{ fontWeight: "bold", fontSize: 16 }}>{timeStr}</Text>
                <Text style={{ color: "gray", fontSize: 14 }}>
                  {event.title || "（タイトルなし）"}
                </Text>
              </View>
            </View>
          );
        })
      )}

      {permissionGranted && !loading && (
        <TouchableOpacity
          onPress={fetchTodayEvents}
          style={{
            marginTop: 20,
            backgroundColor: "#4285F4",
            paddingVertical: 12,
            paddingHorizontal: 20,
            borderRadius: 6,
            alignItems: "center",
          }}
        >
          <Text style={{ color: "white", fontWeight: "bold" }}>再読み込み</Text>
        </TouchableOpacity>
      )}
    </ScrollView>
  );
}
