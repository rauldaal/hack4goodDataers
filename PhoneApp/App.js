import React, { useState, useEffect } from 'react';
import { StyleSheet, View, Text, TouchableWithoutFeedback, Button  } from 'react-native';
import { BarCodeScanner } from 'expo-barcode-scanner';
import { Audio } from 'expo-av';
import * as Speech from 'expo-speech';



var mode = 0;


export default function App() {

  const [hasPermission, setHasPermission] = useState(null);
  const [scanned, setScanned] = useState(false);
  const [codeData, setCodeData] = useState(null);
  const [responseData, setResponseData] = useState(null);
  const [scanQr, setScanQr] = useState(null);


  useEffect(() => {
    (async () => {
      const { status } = await BarCodeScanner.requestPermissionsAsync();
      setHasPermission(status === 'granted');
    })();
  }, []);

    const sendDataToBackend = async (data) => {
      try {
        const response = await fetch('http://192.168.1.117:5000/hello', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
          },
          body: JSON.stringify(data),
        });

        const responseData = await response.json();
        console.log('Response:', responseData['nombre']);
        const message = `<speak>NOMBRE:  ${responseData['nombre']} <break time="1000ms" /> MARCA: ${responseData['marca']}</speak>`
        Speech.speak(message, { language: 'es' });

      } catch (error) {
        console.error('Error:', error);
      }
  }
    
  const playBeep = async () => {
    const { sound } = await Audio.Sound.createAsync(
      require('./assets/beep.mp3')
    );
    await sound.playAsync();
  }
  
  const handleBarCodeScanned = ({ type, data }) => {
    console.log(type)
    console.log(mode)

    if (mode === 0 && type == '32'){
      console.log('READING PRODUCT')
      setScanned(true);
      playBeep();
      const response = sendDataToBackend(data);
      console.log('HOLA')
      console.log(response)
      setCodeData(data);
    }
    else if(mode ===1 && type == '256'){
      console.log(type)
      setScanned(true);
      playBeep();
      console.log('READING LOCATION INFO')
      const message = `<speak>Usted se encuentra en la sección <break time="800ms"/> ${data}</speak>`
      Speech.speak(message, { language: 'es' });
      setCodeData(data);
    }
    else{
      console.log('READING UNSUPPORTED TYPE')
    }
    
  };

  

  const handleScanAgain = () => {
    setScanned(false);
    setCodeData(null);
  };

  const handleScanQr = () => {
    console.log(`Modo cambiado --- ACTUAL ${mode}`)
    setScanQr(false);
    setScanned(false);
    setCodeData(null);
    if (mode === 0){
      mode = 1;
      const message = `<speak>ESCANEANDO UBICACIÓN</speak>`
      Speech.speak(message, { language: 'es' });
    }
    else{
      mode = 0;
      const message = `<speak>ESCANEANDO PRODUCTO</speak>`
      Speech.speak(message, { language: 'es' });
    }
    console.log(`Modo cambiado --- NUEVO ${mode}`)
    
  };

  if (hasPermission === null) {
    return <View />;
  }
  if (hasPermission === false) {
    return <Text>No access to camera</Text>;
  }

  return (
    <View style={styles.container}>
      <View style={styles.scannerContainer}>
        <BarCodeScanner
          onBarCodeScanned={scanned ? undefined : handleBarCodeScanned}
          style={StyleSheet.absoluteFillObject}
        />
      </View>
        {codeData && (
          <View style={styles.codeDataContainer}>
          <>
            <Text style={styles.scanAgainText} onPress={handleScanAgain}>
              Tap to Scan Again
            </Text>
          </> 
        </View>
        ) 
        }
      <View style={styles.changeModeContainer}>
        <Text style={styles.changeModeText} onPress={handleScanQr}>
          Change Mode
        </Text>
      </View>
    </View>
  )
};

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: 'black',
  },
  scannerContainer: {
    flex: 1,
    flexDirection: 'row',
    flexWrap: 'wrap',
  },
  codeDataContainer: {
    position: 'absolute',
    top: 0,
    left: 0,
    right: 0,
    bottom: 120,
    backgroundColor: 'rgba(0, 0, 0, 0.5)',
    alignItems: 'center',
    justifyContent: 'center',
  },
  codeDataText: {
    color: 'white',
    fontSize: 18,
    marginVertical: 10,
  },
  scanAgainText: {
    color: 'white',
    fontSize: 20,
    marginTop: 20,
    textDecorationLine: 'underline',
  },
  changeModeContainer: {
    position: 'absolute',
    bottom: 20,
    left: 0,
    right: 0,
    alignItems: 'center',
  },
  changeModeText: {
    color: 'white',
    fontSize: 20,
    textDecorationLine: 'underline',
    textAlign: 'center',
  },
});
