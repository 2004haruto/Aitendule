import { API_KEY } from '@env';

const BASE_URL = 'https://api.openweathermap.org/data/2.5/weather';

export const fetchWeatherData = async (city) => {
  try {
    const response = await fetch(
      `${BASE_URL}?q=${encodeURIComponent(city)}&appid=${API_KEY}&units=metric&lang=ja`
    );
    const data = await response.json();

    console.log('📦 生データ:', JSON.stringify(data.main));

    return {
      temperature: `${Math.round(data.main.temp)}°C`,       // ← ラベル削除
      high: `${Math.round(data.main.temp_max)}°C`,
      low: `${Math.round(data.main.temp_min)}°C`,
      condition: data.weather[0].description,
      icon: data.weather[0].icon,
    };
  } catch (error) {
    console.error('Weather data fetch error:', error);
    return null;
  }
};
