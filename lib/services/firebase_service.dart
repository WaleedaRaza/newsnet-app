import 'package:firebase_core/firebase_core.dart';
import 'package:firebase_auth/firebase_auth.dart';
import 'package:cloud_firestore/cloud_firestore.dart';
import 'package:firebase_storage/firebase_storage.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';

import '../firebase_options.dart';
import '../models/user_profile.dart';
import '../models/story.dart';
import '../models/fusion_result.dart';
import '../models/chat_message.dart';

class FirebaseService {
  static final FirebaseAuth _auth = FirebaseAuth.instance;
  static final FirebaseFirestore _firestore = FirebaseFirestore.instance;
  static final FirebaseStorage _storage = FirebaseStorage.instance;

  // Collections
  static const String usersCollection = 'users';
  static const String storiesCollection = 'stories';
  static const String fusionResultsCollection = 'fusion_results';
  static const String chatMessagesCollection = 'chat_messages';

  // Initialize Firebase
  static Future<void> initialize() async {
    await Firebase.initializeApp(
      options: DefaultFirebaseOptions.currentPlatform,
    );
  }

  // Authentication methods
  static Future<UserCredential> signUp({
    required String email,
    required String password,
    String? name,
  }) async {
    try {
      final credential = await _auth.createUserWithEmailAndPassword(
        email: email,
        password: password,
      );

      // Create user profile in Firestore
      if (credential.user != null) {
        await _createUserProfile(
          userId: credential.user!.uid,
          email: email,
          name: name,
        );
      }

      return credential;
    } catch (e) {
      throw _handleAuthError(e);
    }
  }

  static Future<UserCredential> signIn({
    required String email,
    required String password,
  }) async {
    try {
      return await _auth.signInWithEmailAndPassword(
        email: email,
        password: password,
      );
    } catch (e) {
      throw _handleAuthError(e);
    }
  }

  static Future<void> signOut() async {
    await _auth.signOut();
  }

  static User? getCurrentUser() {
    return _auth.currentUser;
  }

  static Stream<User?> get authStateChanges => _auth.authStateChanges();

  // User Profile methods
  static Future<void> _createUserProfile({
    required String userId,
    required String email,
    String? name,
  }) async {
    final userProfile = {
      'id': userId,
      'email': email,
      'name': name ?? '',
      'interests': <String>[],
      'beliefFingerprint': <String, dynamic>{},
      'biasSetting': 0.5,
      'createdAt': FieldValue.serverTimestamp(),
      'updatedAt': FieldValue.serverTimestamp(),
    };

    await _firestore
        .collection(usersCollection)
        .doc(userId)
        .set(userProfile);
  }

  static Future<UserProfile> getUserProfile(String userId) async {
    try {
      final doc = await _firestore
          .collection(usersCollection)
          .doc(userId)
          .get();

      if (!doc.exists) {
        throw Exception('User profile not found');
      }

      return UserProfile.fromJson({
        'id': doc.id,
        ...doc.data()!,
      });
    } catch (e) {
      throw Exception('Failed to get user profile: $e');
    }
  }

  static Future<void> updateUserProfile(UserProfile profile) async {
    try {
      await _firestore
          .collection(usersCollection)
          .doc(profile.id)
          .update({
        'name': profile.name,
        'interests': profile.interests,
        'beliefFingerprint': profile.beliefFingerprint,
        'biasSetting': profile.biasSetting,
        'updatedAt': FieldValue.serverTimestamp(),
      });
    } catch (e) {
      throw Exception('Failed to update user profile: $e');
    }
  }

  // Stories methods
  static Future<List<Story>> getStories({
    int limit = 20,
    DocumentSnapshot? lastDocument,
    List<String>? topics,
  }) async {
    try {
      Query query = _firestore
          .collection(storiesCollection)
          .orderBy('publishedAt', descending: true)
          .limit(limit);

      if (topics != null && topics.isNotEmpty) {
        query = query.where('topics', arrayContainsAny: topics);
      }

      if (lastDocument != null) {
        query = query.startAfterDocument(lastDocument);
      }

      final snapshot = await query.get();
      
      return snapshot.docs.map((doc) {
        return Story.fromJson({
          'id': doc.id,
          ...doc.data() as Map<String, dynamic>,
        });
      }).toList();
    } catch (e) {
      throw Exception('Failed to get stories: $e');
    }
  }

  static Future<Story> getStory(String storyId) async {
    try {
      final doc = await _firestore
          .collection(storiesCollection)
          .doc(storyId)
          .get();

      if (!doc.exists) {
        throw Exception('Story not found');
      }

      return Story.fromJson({
        'id': doc.id,
        ...doc.data()!,
      });
    } catch (e) {
      throw Exception('Failed to get story: $e');
    }
  }

  static Future<void> createStory(Story story) async {
    try {
      await _firestore
          .collection(storiesCollection)
          .doc(story.id)
          .set({
        'eventKey': story.eventKey,
        'title': story.title,
        'summaryNeutral': story.summaryNeutral,
        'summaryModulated': story.summaryModulated,
        'sources': story.sources,
        'topics': story.topics,
        'confidence': story.confidence,
        'publishedAt': FieldValue.serverTimestamp(),
        'updatedAt': FieldValue.serverTimestamp(),
      });
    } catch (e) {
      throw Exception('Failed to create story: $e');
    }
  }

  // Fusion Results methods
  static Future<FusionResult> getFusionResult(String storyId, double bias) async {
    try {
      final doc = await _firestore
          .collection(fusionResultsCollection)
          .doc('${storyId}_${bias.toStringAsFixed(2)}')
          .get();

      if (!doc.exists) {
        // Create a mock fusion result if it doesn't exist
        return _createMockFusionResult(storyId, bias);
      }

      return FusionResult.fromJson({
        'id': doc.id,
        ...doc.data()!,
      });
    } catch (e) {
      throw Exception('Failed to get fusion result: $e');
    }
  }

  static Future<void> saveFusionResult(FusionResult result) async {
    try {
      await _firestore
          .collection(fusionResultsCollection)
          .doc(result.id)
          .set({
        'storyId': result.storyId,
        'fusedNarrative': result.fusedNarrative,
        'modulatedNarrative': result.modulatedNarrative,
        'biasLevel': result.biasLevel,
        'confidence': result.confidence,
        'contradictions': result.contradictions.map((c) => c.toJson()).toList(),
        'entities': result.entities.map((e) => e.toJson()).toList(),
        'createdAt': FieldValue.serverTimestamp(),
      });
    } catch (e) {
      throw Exception('Failed to save fusion result: $e');
    }
  }

  // Chat methods
  static Future<List<ChatMessage>> getChatMessages(String storyId) async {
    try {
      final snapshot = await _firestore
          .collection(chatMessagesCollection)
          .where('storyId', isEqualTo: storyId)
          .orderBy('timestamp', descending: true)
          .get();

      return snapshot.docs.map((doc) {
        return ChatMessage.fromJson({
          'id': doc.id,
          ...doc.data() as Map<String, dynamic>,
        });
      }).toList();
    } catch (e) {
      throw Exception('Failed to get chat messages: $e');
    }
  }

  static Future<void> saveChatMessage(ChatMessage message) async {
    try {
      await _firestore
          .collection(chatMessagesCollection)
          .doc(message.id)
          .set({
        'storyId': message.storyId,
        'content': message.content,
        'isUser': message.isUser,
        'timestamp': FieldValue.serverTimestamp(),
        'sourceContext': message.sourceContext,
      });
    } catch (e) {
      throw Exception('Failed to save chat message: $e');
    }
  }

  // Mock data generation
  static FusionResult _createMockFusionResult(String storyId, double bias) {
    final biasLabels = {
      0.0: 'Challenge Me',
      0.25: 'Question',
      0.5: 'Neutral',
      0.75: 'Support',
      1.0: 'Prove Me Right',
    };

    final biasLabel = biasLabels.entries
        .where((entry) => bias <= entry.key)
        .first
        .value;

    return FusionResult(
      id: '${storyId}_${bias.toStringAsFixed(2)}',
      storyId: storyId,
      fusedNarrative: 'This is a comprehensive analysis of the story from multiple perspectives.',
      modulatedNarrative: 'Based on your bias setting ($biasLabel), here is the narrative: This story presents a complex situation that requires careful consideration of multiple viewpoints.',
      biasLevel: bias,
      confidence: 0.85,
      contradictions: [
        Contradiction(
          id: 'cont_1',
          description: 'Different sources report conflicting information about the timeline.',
          sources: ['Source A', 'Source B'],
          resolution: 'Further investigation is needed to clarify the timeline.',
          severity: 0.3,
        ),
      ],
      entities: [
        Entity(
          id: 'ent_1',
          name: 'John Doe',
          type: 'person',
          confidence: 0.9,
          mentions: ['John Doe', 'Mr. Doe'],
        ),
      ],
      createdAt: DateTime.now(),
    );
  }

  // Error handling
  static Exception _handleAuthError(dynamic error) {
    if (error is FirebaseAuthException) {
      switch (error.code) {
        case 'user-not-found':
          return Exception('No user found with this email address.');
        case 'wrong-password':
          return Exception('Wrong password provided.');
        case 'email-already-in-use':
          return Exception('An account already exists with this email address.');
        case 'weak-password':
          return Exception('The password provided is too weak.');
        case 'invalid-email':
          return Exception('The email address is invalid.');
        default:
          return Exception('Authentication failed: ${error.message}');
      }
    }
    return Exception('Authentication failed: $error');
  }
}

// Providers
final firebaseServiceProvider = Provider<FirebaseService>((ref) => FirebaseService());
final firebaseAuthProvider = StreamProvider<User?>((ref) => FirebaseAuth.instance.authStateChanges()); 