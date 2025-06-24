import React, { useState } from 'react';
import { View, TextInput, Button, Text, ActivityIndicator, Alert, StyleSheet } from 'react-native';
import AsyncStorage from '@react-native-async-storage/async-storage';
import { GO_API_BASE_URL } from "@env";
const LoginScreen = ({ navigation }) => {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [loading, setLoading] = useState(false);

  const handleLogin = async () => {
    if (!email || !password) {
      Alert.alert('エラー', 'メールアドレスとパスワードを入力してください。');
      return;
    }

    setLoading(true);
    try {
      const response = await fetch(`${GO_API_BASE_URL}/api/login`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ email, password }),
      });

      console.log('レスポンスステータスコード:', response.status);
      console.log('レスポンス Content-Type:', response.headers.get('content-type'));

      if (!response.ok) {
        const errorMessage = await response.text();
        throw new Error(errorMessage || 'ログインに失敗しました。');
      }

      // JSON レスポンスかどうかをチェックしてパース
      const contentType = response.headers.get('content-type');
      let data;
      if (contentType && contentType.includes('application/json')) {
        data = await response.json();
      } else {
        throw new Error('サーバーのレスポンスが正しい形式ではありません。');
      }

      console.log('ログイン成功のレスポンス:', data);

      const userId = data["user_id"];
      if (!userId) {
        throw new Error('user_id がレスポンスに含まれていません。');
      }

      // AsyncStorage に保存
      await AsyncStorage.setItem('user_id', userId.toString());

      console.log('ユーザーIDが保存されました:', userId);

      // ホーム画面に遷移
      navigation.reset({
        index: 0,
        routes: [{ name: 'Home' }],
      });

    } catch (error) {
      console.error('ネットワークエラー:', error);
      Alert.alert('エラー', error.message || 'ネットワークエラーが発生しました。後でもう一度試してください。');
    } finally {
      setLoading(false);
    }
  };

  return (
    <View style={styles.container}>
      <Text style={styles.title}>ログイン</Text>
      <TextInput
        style={styles.input}
        placeholder="Email"
        value={email}
        onChangeText={setEmail}
        keyboardType="email-address"
        autoCapitalize="none"
      />
      <TextInput
        style={styles.input}
        placeholder="Password"
        value={password}
        secureTextEntry
        onChangeText={setPassword}
      />
      {loading ? (
        <ActivityIndicator size="large" color="#0000ff" />
      ) : (
        <Button title="Login" onPress={handleLogin} />
      )}
      <Text style={styles.signupText} onPress={() => navigation.navigate('Signup')}>
        アカウントをお持ちでないですか？ サインアップ
      </Text>
    </View>
  );
};

const styles = StyleSheet.create({
  container: {
    flex: 1,
    justifyContent: 'center',
    padding: 16,
    backgroundColor: '#f5f5f5',
  },
  title: {
    fontSize: 24,
    fontWeight: 'bold',
    textAlign: 'center',
    marginBottom: 24,
  },
  input: {
    height: 40,
    borderColor: '#ccc',
    borderWidth: 1,
    borderRadius: 5,
    paddingHorizontal: 8,
    marginBottom: 12,
    backgroundColor: '#fff',
  },
  signupText: {
    marginTop: 20,
    textAlign: 'center',
    color: '#0000ff',
  },
});

export default LoginScreen;
