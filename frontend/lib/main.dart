import 'package:flutter/material.dart';
import 'package:http/http.dart' as http;
import 'dart:convert';

void main() {
  runApp(const JournalApp());
}

class JournalApp extends StatelessWidget {
  const JournalApp({super.key});

  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      title: 'AI Journal',
      theme: ThemeData(
        primarySwatch: Colors.blue,
        useMaterial3: true,
      ),
      home: const JournalPage(),
    );
  }
}

class JournalPage extends StatefulWidget {
  const JournalPage({super.key});

  @override
  State<JournalPage> createState() => _JournalPageState();
}

class _JournalPageState extends State<JournalPage> {
  final _feelingController = TextEditingController();
  String _journalEntry = '';
  bool _isLoading = false;

  Future<void> _generateJournal() async {
    setState(() {
      _isLoading = true;
      _journalEntry = '';
    });

    try {
      final response = await http.post(
        Uri.parse('http://localhost:5000/generate-journal'),
        headers: {
          'Content-Type': 'application/json',
        },
        body: json.encode({'feeling': _feelingController.text}),
      );

      if (response.statusCode == 200) {
        setState(() {
          _journalEntry = json.decode(response.body)['journal_entry'];
        });
      } else {
        throw Exception('Failed to generate journal: ${response.statusCode}');
      }
    } catch (e) {
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(content: Text('Error: $e')),
      );
    } finally {
      setState(() {
        _isLoading = false;
      });
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: const Text('AI Journal')),
      body: Padding(
        padding: const EdgeInsets.all(16.0),
        child: Column(
          children: [
            TextField(
              controller: _feelingController,
              decoration: const InputDecoration(
                labelText: 'How are you feeling?',
                border: OutlineInputBorder(),
              ),
              maxLines: 3,
            ),
            const SizedBox(height: 16),
            ElevatedButton(
              onPressed: _isLoading ? null : _generateJournal,
              child: _isLoading
                  ? const CircularProgressIndicator()
                  : const Text('Generate Journal Entry'),
            ),
            const SizedBox(height: 16),
            Expanded(
              child: SingleChildScrollView(
                child: Text(_journalEntry),
              ),
            ),
          ],
        ),
      ),
    );
  }
} 