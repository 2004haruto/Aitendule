const API_KEY = 'APIキー;
const BASE_URL = 'https://api.openweathermap.org/data/2.5/weather';

export const fetchWeatherData = async (city) => {
  try {
    const response = await fetch(`${BASE_URL}?q=${city}&appid=${API_KEY}&units=metric&lang=ja`);
    const data = await response.json();
    return {
      temperature: `現在の気温:${Math.round(data.main.temp)}°C`,
      condition: data.weather[0].description,
      high: `${Math.round(data.main.temp_max)}°C`,
      low: `${Math.round(data.main.temp_min)}°C`,
      icon: data.weather[0].icon,
    };
  } catch (error) {
    console.error('Weather data fetch error:', error);
    return null;
  }
};
