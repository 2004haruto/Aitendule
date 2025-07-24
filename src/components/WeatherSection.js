import React, { useEffect, useState } from 'react';
import { View, Text, TextInput, Button, Modal, ActivityIndicator, TouchableOpacity, Alert } from 'react-native';
import { Picker } from '@react-native-picker/picker';
import { Ionicons } from '@expo/vector-icons';
import AsyncStorage from '@react-native-async-storage/async-storage';
import { fetchWeatherData } from '../api/fetchWeatherData';
import { GO_API_BASE_URL } from "@env";

const getWeatherIconName = (condition) => {
  if (!condition) return 'partly-sunny';
  if (condition.includes('雷')) return 'thunderstorm';
  if (condition.includes('雪')) return 'snow';
  if (condition.includes('霧')) return 'cloud-outline';
  if (condition.includes('大雨') || condition.includes('強い')) return 'rainy';
  if (condition.includes('雨')) return 'cloudy';
  if (condition.includes('くもり')) return 'cloudy';
  if (condition.includes('部分的に晴れ') || condition.includes('晴れ時々曇り')) return 'partly-sunny';
  if (condition.includes('晴れ')) return 'sunny';
  return 'partly-sunny';
};

const fetchUserCities = async (userId) => {
  const response = await fetch(`${GO_API_BASE_URL}/api/users/${userId}/cities`);
  if (!response.ok) throw new Error('都市データの取得に失敗しました');
  return await response.json();
};

const addUserCity = async (userId, cityName) => {
  const response = await fetch(`${GO_API_BASE_URL}/api/users/${userId}/cities`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ city_name: cityName }),
  });
  if (!response.ok) throw new Error('都市の追加に失敗しました');
  return await response.json();
};

const deleteUserCity = async (userId, cityName) => {
  const encodedCityName = encodeURIComponent(cityName); // URLエンコード
  const response = await fetch(`${GO_API_BASE_URL}/api/users/${userId}/cities/name/${encodedCityName}`, {
    method: 'DELETE',
  });
  if (!response.ok) throw new Error('都市の削除に失敗しました');
};

const WeatherSection = () => {
  const [userId, setUserId] = useState(null);
  const [cityList, setCityList] = useState([]);
  const [selectedCity, setSelectedCity] = useState('');
  const [weatherData, setWeatherData] = useState(null);
  const [loading, setLoading] = useState(false);
  const [modalVisible, setModalVisible] = useState(false);
  const [newCityName, setNewCityName] = useState('');

  // ユーザーIDのロード
  useEffect(() => {
    const loadUserId = async () => {
      const storedUserId = await AsyncStorage.getItem('user_id');
      const parsedUserId = parseInt(storedUserId, 10);
      if (!isNaN(parsedUserId)) setUserId(parsedUserId);
      else console.error('無効なuser_id:', storedUserId);
    };
    loadUserId();
  }, []);

  // 都市データの取得
  const loadCities = async () => {
    if (!userId) return;
    try {
      const cities = await fetchUserCities(userId);
      setCityList(cities);
      if (cities.length > 0) {
        // 最初の都市を選択
        setSelectedCity(cities[0].city_name);
        loadWeather(cities[0].city_name); // 最初の都市の天気をロード
      } else {
        setSelectedCity('');
        setWeatherData(null);
      }
    } catch (error) {
      console.error('都市データの取得に失敗:', error);
    }
  };

  useEffect(() => {
    loadCities();
  }, [userId]);

  // 天気データの取得
  const loadWeather = async (city) => {
    if (!city || city === 'add') return;
    setLoading(true);
    console.log('🌤️ 取得中の都市:', city);
    try {
      const data = await fetchWeatherData(city);
      console.log('🌡️ 取得した天気データ:', data);
      setWeatherData({ city: city, ...data });
    } catch (error) {
      console.error('天気の取得に失敗:', error);
      setWeatherData(null);
    } finally {
      setLoading(false);
    }
  };

  // 都市変更時の処理
  const handleCityChange = (itemValue) => {
    setSelectedCity(itemValue);
    if (itemValue !== 'add') {
      loadWeather(itemValue);
    } else {
      setModalVisible(true);
    }
  };

  // 都市追加
  const handleAddCity = async () => {
    if (!newCityName) {
      alert('都市名を入力してください');
      return;
    }
    try {
      await addUserCity(userId, newCityName);
      setModalVisible(false);
      setNewCityName('');
      loadCities(); // 都市追加後にリストを再ロード
    } catch (error) {
      console.error('都市追加に失敗:', error);
      alert('都市の追加に失敗しました');
    }
  };

  // 都市削除
  const handleDeleteCity = () => {
    Alert.alert(
      '確認',
      `「${selectedCity}」を削除しますか？`,
      [
        { text: 'キャンセル', style: 'cancel' },
        {
          text: '削除',
          style: 'destructive',
          onPress: async () => {
            try {
              await deleteUserCity(userId, selectedCity);
              setSelectedCity('');
              setWeatherData(null);
              loadCities(); // 削除後に都市リストを再ロード
            } catch (error) {
              console.error('都市削除に失敗:', error);
              alert('都市の削除に失敗しました');
            }
          }
        }
      ]
    );
  };

  return (
    <View style={[styles.weatherContainer, { alignItems: 'flex-start' }]}>
      <View style={{ flexDirection: 'row', justifyContent: 'space-between', alignItems: 'center', width: '100%' }}>
        <Text style={styles.weatherTitle}>今日の天気</Text>

        <View style={{ flexDirection: 'row', alignItems: 'center' }}>
          <TouchableOpacity onPress={() => loadWeather(selectedCity)}>
            <Ionicons name="refresh" size={28} color="black" style={{ marginRight: 10 }} />
          </TouchableOpacity>

          {selectedCity && selectedCity !== 'add' && (
            <TouchableOpacity onPress={handleDeleteCity}>
              <Text style={{ color: 'red', fontSize: 14 }}>この都市を削除</Text>
            </TouchableOpacity>
          )}
        </View>
      </View>

      <Picker
        selectedValue={selectedCity}
        onValueChange={handleCityChange}
        style={{ height: 50, width: 200, alignSelf: 'flex-end' }}
      >
        {cityList.map(({ city_name }) => (
          <Picker.Item label={city_name} value={city_name} key={city_name} />
        ))}
        <Picker.Item label="都市を追加" value="add" />
      </Picker>

      {modalVisible && (
        <Modal animationType="slide" transparent={true} visible={modalVisible} onRequestClose={() => setModalVisible(false)}>
          <View style={styles.modalContainer}>
            <View style={styles.modalContent}>
              <Text>新しい都市を追加</Text>
              <TextInput
                value={newCityName}
                onChangeText={setNewCityName}
                placeholder="都市名"
                style={styles.input}
              />
              <Button title="追加" onPress={handleAddCity} />
              <Button title="キャンセル" onPress={() => setModalVisible(false)} />
            </View>
          </View>
        </Modal>
      )}

      {loading ? (
        <ActivityIndicator size="small" />
      ) : weatherData ? (
        <View style={[styles.weatherBox, { alignItems: 'flex-start' }]}>
          <Text style={styles.weatherCity}>{weatherData.city}</Text>
          <View style={{ flexDirection: 'row', alignItems: 'center', marginBottom: 8 }}>
            <Ionicons
              name={getWeatherIconName(weatherData.condition)}
              size={32}
              color="#333"
              style={{ marginRight: 8 }}
            />
            <Text style={styles.weatherCondition}>{weatherData.condition}</Text>
          </View>
          <Text style={styles.weatherTemperature}>現在の気温: {weatherData.temperature}</Text>
          <View style={{ flexDirection: 'row', justifyContent: 'flex-start' }}>
            <Text style={[styles.weatherHighLow, { color: 'red', marginRight: 4 }]}>最高: {weatherData.high}</Text>
            <Text style={[styles.weatherHighLow, { color: 'blue' }]}>最低: {weatherData.low}</Text>
          </View>
        </View>
      ) : (
        <Text>天気データを取得できませんでした</Text>
      )}
    </View>
  );
};

export default WeatherSection;

import { StyleSheet } from 'react-native';

const styles = StyleSheet.create({
  modalContainer: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
    backgroundColor: 'rgba(0, 0, 0, 0.4)',
  },
  modalContent: {
    width: 300,
    backgroundColor: 'white',
    padding: 20,
    borderRadius: 10,
    alignItems: 'center',
  },
  input: {
    width: '100%',
    borderColor: '#ccc',
    borderWidth: 1,
    padding: 10,
    marginVertical: 10,
    borderRadius: 5,
  },
});
