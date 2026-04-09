import React, { useEffect, useState } from "react";
import { SafeAreaView, ScrollView, Text, View } from "react-native";

export default function App() {
  const [status, setStatus] = useState("Connecting...");

  useEffect(() => {
    fetch("http://localhost:8000/")
      .then((res) => res.json())
      .then((data) => setStatus(`API: ${data.app} (${data.status})`))
      .catch(() => setStatus("API unavailable"));
  }, []);

  return (
    <SafeAreaView>
      <ScrollView contentContainerStyle={{ padding: 24 }}>
        <Text style={{ fontSize: 24, fontWeight: "700" }}>SocietyMan Mobile</Text>
        <Text style={{ marginTop: 8 }}>{status}</Text>
        <View style={{ marginTop: 16 }}>
          <Text>• Visitor approvals</Text>
          <Text>• Bill payment and reminders</Text>
          <Text>• Complaint tracking</Text>
          <Text>• Notice feed</Text>
        </View>
      </ScrollView>
    </SafeAreaView>
  );
}
