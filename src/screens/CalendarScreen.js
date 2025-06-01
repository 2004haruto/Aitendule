import React, { useEffect, useState } from "react";
import {
  View,
  Text,
  ScrollView,
  ActivityIndicator,
  Alert,
  StyleSheet,
  TouchableOpacity,
  Modal,
  TouchableWithoutFeedback,
  Dimensions,
  PanResponder,
} from "react-native";
import * as Calendar from "expo-calendar";

const screenHeight = Dimensions.get("window").height;

export default function CalendarScreen() {
  const [eventsMap, setEventsMap] = useState({});
  const [holidays, setHolidays] = useState(new Set());
  const [loading, setLoading] = useState(true);
  const [calendarColorMap, setCalendarColorMap] = useState({});
  const [year, setYear] = useState(new Date().getFullYear());
  const [month, setMonth] = useState(new Date().getMonth());
  const [modalVisible, setModalVisible] = useState(false);
  const [selectedDate, setSelectedDate] = useState(null);

  useEffect(() => {
    fetchHolidays();
  }, []);

  useEffect(() => {
    if (holidays.size > 0) {
      fetchCalendarsAndEvents(holidays);
    }
  }, [year, month]);

  const formatLocalDate = (date) => {
    const y = date.getFullYear();
    const m = ("0" + (date.getMonth() + 1)).slice(-2);
    const d = ("0" + date.getDate()).slice(-2);
    return `${y}-${m}-${d}`;
  };

  const fetchHolidays = async () => {
    try {
      const y = new Date().getFullYear();
      const res = await fetch(`https://date.nager.at/api/v3/PublicHolidays/${y}/JP`);
      if (!res.ok) throw new Error("祝日API取得失敗");
      const data = await res.json();
      const holidaySet = new Set(data.map((h) => h.date));
      setHolidays(holidaySet);
      await fetchCalendarsAndEvents(holidaySet);
    } catch (e) {
      Alert.alert("祝日情報の取得に失敗しました", e.message);
      setLoading(false);
    }
  };

  const fetchCalendarsAndEvents = async (holidaySet) => {
    setLoading(true);
    try {
      const { status } = await Calendar.requestCalendarPermissionsAsync();
      if (status !== "granted") {
        Alert.alert("カレンダーアクセスが拒否されました");
        setLoading(false);
        return;
      }

      const calendars = await Calendar.getCalendarsAsync();
      const colorMap = {};
      calendars.forEach((cal) => {
        colorMap[cal.id] = cal.color || "#007AFF";
      });
      setCalendarColorMap(colorMap);

      const calendarIds = calendars.map((c) => c.id);
      const start = new Date(year, month, 1);
      const end = new Date(year, month + 1, 0, 23, 59, 59, 999);

      let allEvents = [];
      for (let id of calendarIds) {
        const evs = await Calendar.getEventsAsync([id], start, end);
        allEvents.push(...evs);
      }

      const uniqueEvents = Array.from(
        new Map(
          allEvents.map((e) => [`${e.id}_${e.startDate}_${e.title}`, e])
        ).values()
      );

      const map = {};
      uniqueEvents.forEach((e) => {
        const dayKey = formatLocalDate(new Date(e.startDate));
        if (!map[dayKey]) map[dayKey] = [];
        map[dayKey].push(e);
      });

      setEventsMap(map);
    } catch (e) {
      Alert.alert("予定の取得中にエラーが発生しました", e.message);
    } finally {
      setLoading(false);
    }
  };

  const getCellBackgroundColor = (date) => {
    if (!date) return "transparent";
    const dayKey = formatLocalDate(date);
    const todayKey = formatLocalDate(new Date());
    const dayOfWeek = date.getDay();
    if (dayKey === todayKey) return "#d1f5d3"; // 今日
    if (holidays.has(dayKey) || dayOfWeek === 0) return "#ffe6e6"; // 祝日または日曜
    if (dayOfWeek === 6) return "#e6f0ff"; // 土曜
    return "transparent";
  };

  const getDaysArray = (year, month) => {
    const date = new Date(year, month, 1);
    const days = [];
    while (date.getMonth() === month) {
      days.push(new Date(date));
      date.setDate(date.getDate() + 1);
    }
    return days;
  };

  const days = getDaysArray(year, month);
  const weekDays = ["日", "月", "火", "水", "木", "金", "土"];
  const firstDayWeek = new Date(year, month, 1).getDay();
  const blanks = new Array(firstDayWeek).fill(null);

  const handlePrevMonth = () => {
    if (month === 0) {
      setYear(year - 1);
      setMonth(11);
    } else {
      setMonth(month - 1);
    }
  };

  const handleNextMonth = () => {
    if (month === 11) {
      setYear(year + 1);
      setMonth(0);
    } else {
      setMonth(month + 1);
    }
  };

  const openModal = (date) => {
    setSelectedDate(date);
    setModalVisible(true);
  };

  const closeModal = () => {
    setModalVisible(false);
    setSelectedDate(null);
  };

  const panResponder = React.useRef(
    PanResponder.create({
      onStartShouldSetPanResponder: () => true,
      onMoveShouldSetPanResponder: (_, gestureState) => gestureState.dy > 10,
      onPanResponderRelease: (_, gestureState) => {
        if (gestureState.dy > 50) closeModal();
      },
    })
  ).current;

  return (
    <ScrollView style={{ flex: 1, padding: 16 }}>
      <View style={styles.navRow}>
        <TouchableOpacity onPress={handlePrevMonth} style={styles.navButton}>
          <Text style={{ fontSize: 18 }}>‹</Text>
        </TouchableOpacity>
        <Text style={styles.navTitle}>
          {year}年 {month + 1}月の予定
        </Text>
        <TouchableOpacity onPress={handleNextMonth} style={styles.navButton}>
          <Text style={{ fontSize: 18 }}>›</Text>
        </TouchableOpacity>
      </View>

      <View style={{ flexDirection: "row" }}>
        {weekDays.map((wd, i) => {
          let bgColor = "transparent";
          if (i === 0) bgColor = "#ffe6e6";
          else if (i === 6) bgColor = "#e6f0ff";
          return (
            <View key={wd} style={[styles.cell, { backgroundColor: bgColor }]}>
              <Text style={{ textAlign: "center", fontWeight: "bold" }}>{wd}</Text>
            </View>
          );
        })}
      </View>

      <View style={{ flexDirection: "row", flexWrap: "wrap" }}>
        {blanks.map((_, i) => (
          <View key={"blank-" + i} style={styles.cell} />
        ))}

        {loading ? (
          <ActivityIndicator size="large" color="#0000ff" style={{ marginTop: 20, flexBasis: "100%" }} />
        ) : days.length === 0 ? (
          <Text>今月の予定はありません</Text>
        ) : (
          days.map((date) => {
            const dayNum = date.getDate();
            const key = formatLocalDate(date);
            const dayEvents = eventsMap[key] || [];
            const bgColor = getCellBackgroundColor(date);
            const isToday = key === formatLocalDate(new Date());

            return (
              <TouchableOpacity
                key={key}
                style={[styles.cell, isToday && styles.todayCell, { backgroundColor: bgColor }]}
                onPress={() => openModal(date)}
                activeOpacity={0.7}
              >
                <Text style={{ fontWeight: "bold", color: isToday ? "#2c7a00" : "black", marginBottom: 2 }}>
                  {dayNum}
                </Text>
                {dayEvents.slice(0, 2).map((ev) => {
                  const color = calendarColorMap[ev.calendarId] || "gray";
                  return (
                    <Text key={ev.id} style={{ fontSize: 10, color }} numberOfLines={1}>
                      ・{ev.title || "（タイトルなし）"}
                    </Text>
                  );
                })}
                {dayEvents.length > 2 && (
                  <Text style={{ fontSize: 10, color: "gray" }}>...他{dayEvents.length - 2}件</Text>
                )}
              </TouchableOpacity>
            );
          })
        )}
      </View>

      <Modal visible={modalVisible} animationType="slide" transparent onRequestClose={closeModal}>
        <TouchableWithoutFeedback onPress={closeModal}>
          <View style={styles.modalOverlay} />
        </TouchableWithoutFeedback>

        <View style={styles.modalContentContainer} {...panResponder.panHandlers}>
          <Text style={styles.modalTitle}>
            {selectedDate ? `${selectedDate.getFullYear()}年${selectedDate.getMonth() + 1}月${selectedDate.getDate()}日の予定` : ""}
          </Text>
          <ScrollView style={styles.modalScrollView}>
            {(selectedDate ? eventsMap[formatLocalDate(selectedDate)] || [] : []).map((ev) => (
              <View key={ev.id} style={styles.eventItem}>
                <Text style={[styles.eventTitle, { color: calendarColorMap[ev.calendarId] || "black" }]}>
                  {ev.title || "（タイトルなし）"}
                </Text>
                <Text style={styles.eventTime}>
                  {new Date(ev.startDate).toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" })} 〜{" "}
                  {new Date(ev.endDate).toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" })}
                </Text>
                {ev.location ? <Text style={styles.eventLocation}>{ev.location}</Text> : null}
              </View>
            ))}
            {selectedDate && (eventsMap[formatLocalDate(selectedDate)] || []).length === 0 && (
              <Text style={{ fontStyle: "italic", color: "gray" }}>予定はありません</Text>
            )}
          </ScrollView>
          <TouchableOpacity onPress={closeModal} style={styles.closeButton}>
            <Text style={{ color: "white", fontWeight: "bold" }}>閉じる</Text>
          </TouchableOpacity>
        </View>
      </Modal>
    </ScrollView>
  );
}

const styles = StyleSheet.create({
  cell: {
    width: "14.28%",
    borderWidth: 1,
    borderColor: "#ccc",
    padding: 4,
    minHeight: 70,
  },
  todayCell: {
    borderColor: "#2c7a00",
    borderWidth: 2,
  },
  navRow: {
    flexDirection: "row",
    justifyContent: "space-between",
    marginBottom: 12,
    alignItems: "center",
  },
  navButton: {
    padding: 8,
  },
  navTitle: {
    fontSize: 18,
    fontWeight: "bold",
  },
  modalOverlay: {
    flex: 1,
    backgroundColor: "rgba(0,0,0,0.3)",
  },
  modalContentContainer: {
    position: "absolute",
    bottom: 0,
    height: screenHeight * 0.5,
    width: "100%",
    backgroundColor: "white",
    borderTopLeftRadius: 12,
    borderTopRightRadius: 12,
    paddingHorizontal: 16,
    paddingTop: 12,
    paddingBottom: 32,
    shadowColor: "#000",
    shadowOffset: { width: 0, height: -3 },
    shadowOpacity: 0.3,
    shadowRadius: 5,
    elevation: 10,
  },
  modalTitle: {
    fontSize: 16,
    fontWeight: "bold",
    marginBottom: 8,
  },
  modalScrollView: {
    flex: 1,
  },
  eventItem: {
    marginBottom: 10,
  },
  eventTitle: {
    fontWeight: "bold",
  },
  eventTime: {
    fontSize: 12,
    color: "#666",
  },
  eventLocation: {
    fontSize: 12,
    color: "#666",
  },
  closeButton: {
    backgroundColor: "#007AFF",
    padding: 12,
    borderRadius: 8,
    alignItems: "center",
    marginVertical: 8,
  },
});
