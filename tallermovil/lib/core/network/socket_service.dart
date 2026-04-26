import 'dart:async';
import 'dart:convert';
import 'package:flutter/foundation.dart';
import 'package:web_socket_channel/web_socket_channel.dart';
import '../storage/local_storage.dart';
import 'api_client.dart';

class SocketService {
  static final SocketService _instance = SocketService._internal();
  factory SocketService() => _instance;
  SocketService._internal();

  WebSocketChannel? _channel;
  final _controller = StreamController<Map<String, dynamic>>.broadcast();
  bool _isConnected = false;
  Timer? _reconnectTimer;
  int _retryCount = 0;
  static const int maxRetries = 3;

  Stream<Map<String, dynamic>> get stream => _controller.stream;
  bool get isConnected => _isConnected;

  Future<void> connect() async {
    // Si ya estamos conectados o intentando conectar, no hacer nada
    if (_isConnected || (_reconnectTimer?.isActive ?? false)) return;
    
    final storage = LocalStorage();
    final userId = await storage.getUserId();
    
    if (userId == null) {
      debugPrint('SocketService: No UserID found.');
      return;
    }

    final wsUrl = ApiClient.serverUrl.replaceFirst('http', 'ws');
    final url = '$wsUrl/api/v1/ws/$userId';

    debugPrint('SocketService: Attempting connection to $url (Retry: $_retryCount)');

    try {
      _channel = WebSocketChannel.connect(Uri.parse(url));
      
      _isConnected = true;
      debugPrint('SocketService: Connected ✅');
      
      _channel!.stream.listen(
        (message) {
          _retryCount = 0; // Reset retries on success
          
          try {
            final data = jsonDecode(message as String);
            _controller.add(data);
          } catch (e) {
            debugPrint('SocketService: Error decoding message: $e');
          }
        },
        onError: (error) {
          debugPrint('SocketService: Error: $error');
          _handleDisconnect();
        },
        onDone: () {
          debugPrint('SocketService: Connection closed.');
          _handleDisconnect();
        },
        cancelOnError: true,
      );
    } catch (e) {
      debugPrint('SocketService: Failed to connect: $e');
      _handleDisconnect();
    }
  }

  void _handleDisconnect() {
    _isConnected = false;
    _channel?.sink.close();
    
    if (_retryCount < maxRetries) {
      _retryCount++;
      _reconnect();
    } else {
      debugPrint('SocketService: Max retries reached. Stopping reconnection.');
    }
  }

  void _reconnect() {
    _reconnectTimer?.cancel();
    debugPrint('SocketService: Reconnecting in 5 seconds...');
    _reconnectTimer = Timer(const Duration(seconds: 5), () {
      connect();
    });
  }

  void disconnect() {
    debugPrint('SocketService: Manually disconnecting...');
    _reconnectTimer?.cancel();
    _retryCount = 0;
    _isConnected = false;
    _channel?.sink.close();
  }

  void dispose() {
    disconnect();
    _controller.close();
  }
}
