import 'package:flutter/material.dart';
import 'package:http/http.dart' as http;
import 'dart:convert';
import 'dart:ui'; // For backdrop filter if needed

void main() => runApp(const FortressApp());

class FortressApp extends StatelessWidget {
  const FortressApp({super.key});
  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      debugShowCheckedModeBanner: false,
      title: 'DroidSecurity',
      theme: ThemeData.dark().copyWith(
        scaffoldBackgroundColor: const Color(0xFF0F172A), // Dark Slate
        primaryColor: const Color(0xFF6366F1), // Indigo
        cardColor: const Color(0xFF1E293B), // Slate 800
        textTheme: const TextTheme(
          bodyMedium: TextStyle(color: Color(0xFFCBD5E1)),
          titleLarge: TextStyle(
            fontWeight: FontWeight.bold,
            color: Colors.white,
          ),
        ),
        appBarTheme: const AppBarTheme(
          backgroundColor: Colors.transparent,
          elevation: 0,
          centerTitle: true,
          titleTextStyle: TextStyle(
            fontSize: 24,
            fontWeight: FontWeight.w900,
            letterSpacing: 1.2,
            color: Colors.white,
          ),
        ),
      ),
      home: const Dashboard(),
    );
  }
}

class Dashboard extends StatefulWidget {
  const Dashboard({super.key});
  @override
  State<Dashboard> createState() => _DashboardState();
}

class _DashboardState extends State<Dashboard> {
  bool _isAuditing = false;
  String _statusMsg = "System Secure";
  final String _baseUrl = "https://zack-prediastolic-antwan.ngrok-free.dev";

  // --- AUTOMATED AUDIT & NAVIGATION ---
  Future<void> _runAuditCycle(String category) async {
    setState(() {
      _isAuditing = true;
      _statusMsg = "Scanning $category...";
    });

    try {
      // 1. Trigger the agent
      await http
          .get(Uri.parse("$_baseUrl/run-agent?category=$category"))
          .timeout(const Duration(seconds: 5)); // Increased timeout slightly
    } catch (_) {
      // It's okay if this times out, the agent runs in background
    }

    // 2. Start Automatic Polling
    int attempts = 0;
    while (_isAuditing && attempts < 12) {
      // Poll for ~1 minute
      await Future.delayed(const Duration(seconds: 5));
      attempts++;
      try {
        final res = await http.get(Uri.parse("$_baseUrl/get-latest"));
        if (res.statusCode == 200) {
          final data = json.decode(res.body);
          // Check if this report matches the category we just requested
          if (data['status'] == 'success' &&
              data['category'].toString().toLowerCase() ==
                  category.toLowerCase()) {
            if (!mounted) return;
            setState(() => _isAuditing = false);
            _navigateToReport(data);
            break;
          }
        }
      } catch (e) {
        print("Polling error: $e");
      }
    }

    if (mounted && _isAuditing) {
      setState(() {
        _isAuditing = false;
        _statusMsg = "Audit timed out. Try fetching manually.";
      });
      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(
          content: Text("Audit timed out. Please check fetching manually."),
        ),
      );
    }
  }

  // --- MANUAL FETCH BUTTON ---
  Future<void> _manualFetch() async {
    setState(() => _statusMsg = "Fetching latest report...");
    try {
      final res = await http.get(Uri.parse("$_baseUrl/get-latest"));
      final data = json.decode(res.body);
      if (data['status'] == 'success') {
        _navigateToReport(data);
      } else {
        if (!mounted) return;
        ScaffoldMessenger.of(context).showSnackBar(
          const SnackBar(
            content: Text("No new report found. Start an audit first."),
            backgroundColor: Colors.orange,
          ),
        );
      }
    } catch (e) {
      if (!mounted) return;
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(
          content: Text("Fetch failed: ${e.toString()}"),
          backgroundColor: Colors.red,
        ),
      );
    } finally {
      if (mounted) setState(() => _statusMsg = "System Secure");
    }
  }

  void _navigateToReport(Map<String, dynamic> data) {
    Navigator.push(
      context,
      MaterialPageRoute(builder: (context) => ReportPage(data: data)),
    );
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      extendBodyBehindAppBar: true,
      appBar: AppBar(title: const Text("🛡️ FORTRESS AI")),
      body: Stack(
        children: [
          // Background Gradient
          Container(
            decoration: const BoxDecoration(
              gradient: LinearGradient(
                begin: Alignment.topLeft,
                end: Alignment.bottomRight,
                colors: [Color(0xFF0F172A), Color(0xFF1E1B4B)],
              ),
            ),
          ),

          SafeArea(
            child: Padding(
              padding: const EdgeInsets.symmetric(
                horizontal: 24.0,
                vertical: 20,
              ),
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  const Text(
                    "Security Hub",
                    style: TextStyle(fontSize: 18, color: Colors.grey),
                  ),
                  const SizedBox(height: 20),
                  Expanded(
                    child: GridView.count(
                      crossAxisCount: 2,
                      crossAxisSpacing: 20,
                      mainAxisSpacing: 20,
                      children: [
                        _card(
                          "Camera",
                          Icons.camera_alt_outlined,
                          Colors.orange,
                          "camera",
                        ),
                        _card(
                          "Microphone",
                          Icons.mic_none_outlined,
                          Colors.redAccent,
                          "microphone",
                        ),
                        _card(
                          "Location",
                          Icons.location_on_outlined,
                          Colors.blueAccent,
                          "location",
                        ),
                        _card(
                          "SMS",
                          Icons.sms_outlined,
                          Colors.greenAccent,
                          "sms",
                        ),
                      ],
                    ),
                  ),
                  const SizedBox(height: 30),
                  // Manual Fetch / View Report Button
                  InkWell(
                    onTap: _isAuditing ? null : _manualFetch,
                    borderRadius: BorderRadius.circular(20),
                    child: Container(
                      height: 70,
                      width: double.infinity,
                      decoration: BoxDecoration(
                        gradient: const LinearGradient(
                          colors: [Color(0xFF6366F1), Color(0xFF818CF8)],
                        ),
                        borderRadius: BorderRadius.circular(20),
                        boxShadow: [
                          BoxShadow(
                            color: const Color(0xFF6366F1).withOpacity(0.4),
                            blurRadius: 15,
                            offset: const Offset(0, 5),
                          ),
                        ],
                      ),
                      child: Row(
                        mainAxisAlignment: MainAxisAlignment.center,
                        children: const [
                          Icon(
                            Icons.description_outlined,
                            color: Colors.white,
                            size: 28,
                          ),
                          SizedBox(width: 12),
                          Text(
                            "VIEW LATEST REPORT",
                            style: TextStyle(
                              color: Colors.white,
                              fontWeight: FontWeight.bold,
                              fontSize: 18,
                              letterSpacing: 1,
                            ),
                          ),
                        ],
                      ),
                    ),
                  ),
                ],
              ),
            ),
          ),

          // Loading Overlay
          if (_isAuditing) _buildLoadingOverlay(),
        ],
      ),
    );
  }

  Widget _buildLoadingOverlay() {
    return Container(
      color: Colors.black54,
      child: BackdropFilter(
        filter: ImageFilter.blur(sigmaX: 5, sigmaY: 5),
        child: Center(
          child: Container(
            padding: const EdgeInsets.all(30),
            decoration: BoxDecoration(
              color: const Color(0xFF1E293B),
              borderRadius: BorderRadius.circular(20),
              boxShadow: const [
                BoxShadow(color: Colors.black45, blurRadius: 20),
              ],
            ),
            child: Column(
              mainAxisSize: MainAxisSize.min,
              children: [
                const CircularProgressIndicator(color: Color(0xFF6366F1)),
                const SizedBox(height: 20),
                Text(
                  _statusMsg,
                  style: const TextStyle(
                    fontWeight: FontWeight.bold,
                    fontSize: 16,
                  ),
                ),
              ],
            ),
          ),
        ),
      ),
    );
  }

  Widget _card(String name, IconData icon, Color color, String category) =>
      InkWell(
        onTap: () => _runAuditCycle(category),
        borderRadius: BorderRadius.circular(24),
        child: Container(
          decoration: BoxDecoration(
            color: const Color(0xFF1E293B),
            borderRadius: BorderRadius.circular(24),
            border: Border.all(color: Colors.white.withOpacity(0.05)),
            boxShadow: [
              BoxShadow(
                color: Colors.black.withOpacity(0.2),
                blurRadius: 10,
                offset: const Offset(0, 4),
              ),
            ],
          ),
          child: Column(
            mainAxisAlignment: MainAxisAlignment.center,
            children: [
              Container(
                padding: const EdgeInsets.all(16),
                decoration: BoxDecoration(
                  color: color.withOpacity(0.15),
                  shape: BoxShape.circle,
                ),
                child: Icon(icon, color: color, size: 32),
              ),
              const SizedBox(height: 16),
              Text(
                name,
                style: const TextStyle(
                  fontWeight: FontWeight.w600,
                  fontSize: 16,
                  letterSpacing: 0.5,
                ),
              ),
            ],
          ),
        ),
      );
}

// --- REPORT PAGE ---
class ReportPage extends StatelessWidget {
  final Map<String, dynamic> data;
  const ReportPage({super.key, required this.data});

  @override
  Widget build(BuildContext context) {
    final report = data['data'];
    final List apps = report != null ? report['apps'] : [];
    final String summary = report != null
        ? report['summary']
        : "No summary available.";
    final String category =
        data['category']?.toString().toUpperCase() ?? "AUDIT";

    return Scaffold(
      backgroundColor: const Color(0xFF0F172A),
      appBar: AppBar(
        title: Text("$category REPORT"),
        centerTitle: true,
        backgroundColor: const Color(0xFF1E293B),
      ),
      body: SingleChildScrollView(
        child: Padding(
          padding: const EdgeInsets.all(20.0),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.stretch,
            children: [
              // SUMMARY CARD
              Container(
                padding: const EdgeInsets.all(24),
                decoration: BoxDecoration(
                  gradient: const LinearGradient(
                    colors: [Color(0xFF334155), Color(0xFF1E293B)],
                    begin: Alignment.topLeft,
                    end: Alignment.bottomRight,
                  ),
                  borderRadius: BorderRadius.circular(20),
                  boxShadow: [
                    BoxShadow(
                      color: Colors.black.withOpacity(0.2),
                      blurRadius: 10,
                      offset: const Offset(0, 5),
                    ),
                  ],
                ),
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Row(
                      children: const [
                        Icon(
                          Icons.analytics_outlined,
                          color: Colors.blueAccent,
                          size: 28,
                        ),
                        SizedBox(width: 10),
                        Text(
                          "Audit Summary",
                          style: TextStyle(
                            fontSize: 20,
                            fontWeight: FontWeight.bold,
                          ),
                        ),
                      ],
                    ),
                    const SizedBox(height: 15),
                    Text(
                      summary,
                      style: const TextStyle(
                        fontSize: 16,
                        height: 1.5,
                        color: Color(0xFFE2E8F0),
                      ),
                    ),
                  ],
                ),
              ),

              const SizedBox(height: 25),
              const Text(
                "Detailed Breakdown",
                style: TextStyle(
                  fontSize: 18,
                  fontWeight: FontWeight.bold,
                  color: Colors.grey,
                ),
              ),
              const SizedBox(height: 15),

              // APPS LIST
              ...apps.map((app) {
                final String risk = app['risk_level'].toString().toLowerCase();
                Color riskColor;
                IconData riskIcon;

                if (risk.contains("safe")) {
                  riskColor = Colors.greenAccent;
                  riskIcon = Icons.check_circle_outline;
                } else if (risk.contains("normal")) {
                  riskColor = Colors.blueAccent;
                  riskIcon = Icons.info_outline;
                } else {
                  riskColor = Colors.orangeAccent;
                  riskIcon = Icons.warning_amber_rounded;
                }

                if (risk.contains("risky") || risk.contains("danger")) {
                  riskColor = Colors.redAccent;
                }

                return Container(
                  margin: const EdgeInsets.only(bottom: 12),
                  decoration: BoxDecoration(
                    color: const Color(0xFF1E293B),
                    borderRadius: BorderRadius.circular(16),
                    border: Border.all(color: Colors.white.withOpacity(0.05)),
                  ),
                  child: ListTile(
                    contentPadding: const EdgeInsets.symmetric(
                      horizontal: 20,
                      vertical: 8,
                    ),
                    leading: Container(
                      padding: const EdgeInsets.all(10),
                      decoration: BoxDecoration(
                        color: riskColor.withOpacity(0.1),
                        shape: BoxShape.circle,
                      ),
                      child: Icon(riskIcon, color: riskColor),
                    ),
                    title: Text(
                      app['app_name'],
                      style: const TextStyle(
                        fontWeight: FontWeight.bold,
                        fontSize: 16,
                      ),
                    ),
                    subtitle: Padding(
                      padding: const EdgeInsets.only(top: 4.0),
                      child: Text(
                        app['reason'],
                        style: TextStyle(color: Colors.grey[400]),
                      ),
                    ),
                    trailing: Container(
                      padding: const EdgeInsets.symmetric(
                        horizontal: 10,
                        vertical: 5,
                      ),
                      decoration: BoxDecoration(
                        color: riskColor.withOpacity(0.1),
                        borderRadius: BorderRadius.circular(10),
                        border: Border.all(color: riskColor.withOpacity(0.5)),
                      ),
                      child: Text(
                        app['risk_level'].toUpperCase(),
                        style: TextStyle(
                          color: riskColor,
                          fontWeight: FontWeight.bold,
                          fontSize: 12,
                        ),
                      ),
                    ),
                  ),
                );
              }).toList(),

              const SizedBox(height: 40),
            ],
          ),
        ),
      ),
    );
  }
}
