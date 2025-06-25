// GENERATED CODE - DO NOT MODIFY BY HAND

part of 'story_provider.dart';

// **************************************************************************
// RiverpodGenerator
// **************************************************************************

String _$storyHash() => r'1bfade301098f71c2fbeebe7968098d85f0620db';

/// Copied from Dart SDK
class _SystemHash {
  _SystemHash._();

  static int combine(int hash, int value) {
    // ignore: parameter_assignments
    hash = 0x1fffffff & (hash + value);
    // ignore: parameter_assignments
    hash = 0x1fffffff & (hash + ((0x0007ffff & hash) << 10));
    return hash ^ (hash >> 6);
  }

  static int finish(int hash) {
    // ignore: parameter_assignments
    hash = 0x1fffffff & (hash + ((0x03ffffff & hash) << 3));
    // ignore: parameter_assignments
    hash = hash ^ (hash >> 11);
    return 0x1fffffff & (hash + ((0x00003fff & hash) << 15));
  }
}

/// See also [story].
@ProviderFor(story)
const storyProvider = StoryFamily();

/// See also [story].
class StoryFamily extends Family<AsyncValue<Story>> {
  /// See also [story].
  const StoryFamily();

  /// See also [story].
  StoryProvider call(
    String storyId,
  ) {
    return StoryProvider(
      storyId,
    );
  }

  @override
  StoryProvider getProviderOverride(
    covariant StoryProvider provider,
  ) {
    return call(
      provider.storyId,
    );
  }

  static const Iterable<ProviderOrFamily>? _dependencies = null;

  @override
  Iterable<ProviderOrFamily>? get dependencies => _dependencies;

  static const Iterable<ProviderOrFamily>? _allTransitiveDependencies = null;

  @override
  Iterable<ProviderOrFamily>? get allTransitiveDependencies =>
      _allTransitiveDependencies;

  @override
  String? get name => r'storyProvider';
}

/// See also [story].
class StoryProvider extends AutoDisposeFutureProvider<Story> {
  /// See also [story].
  StoryProvider(
    String storyId,
  ) : this._internal(
          (ref) => story(
            ref as StoryRef,
            storyId,
          ),
          from: storyProvider,
          name: r'storyProvider',
          debugGetCreateSourceHash:
              const bool.fromEnvironment('dart.vm.product')
                  ? null
                  : _$storyHash,
          dependencies: StoryFamily._dependencies,
          allTransitiveDependencies: StoryFamily._allTransitiveDependencies,
          storyId: storyId,
        );

  StoryProvider._internal(
    super._createNotifier, {
    required super.name,
    required super.dependencies,
    required super.allTransitiveDependencies,
    required super.debugGetCreateSourceHash,
    required super.from,
    required this.storyId,
  }) : super.internal();

  final String storyId;

  @override
  Override overrideWith(
    FutureOr<Story> Function(StoryRef provider) create,
  ) {
    return ProviderOverride(
      origin: this,
      override: StoryProvider._internal(
        (ref) => create(ref as StoryRef),
        from: from,
        name: null,
        dependencies: null,
        allTransitiveDependencies: null,
        debugGetCreateSourceHash: null,
        storyId: storyId,
      ),
    );
  }

  @override
  AutoDisposeFutureProviderElement<Story> createElement() {
    return _StoryProviderElement(this);
  }

  @override
  bool operator ==(Object other) {
    return other is StoryProvider && other.storyId == storyId;
  }

  @override
  int get hashCode {
    var hash = _SystemHash.combine(0, runtimeType.hashCode);
    hash = _SystemHash.combine(hash, storyId.hashCode);

    return _SystemHash.finish(hash);
  }
}

@Deprecated('Will be removed in 3.0. Use Ref instead')
// ignore: unused_element
mixin StoryRef on AutoDisposeFutureProviderRef<Story> {
  /// The parameter `storyId` of this provider.
  String get storyId;
}

class _StoryProviderElement extends AutoDisposeFutureProviderElement<Story>
    with StoryRef {
  _StoryProviderElement(super.provider);

  @override
  String get storyId => (origin as StoryProvider).storyId;
}

String _$fusionResultHash() => r'e8cd1653e733b8b372ce6c44230bb17609769cba';

/// See also [fusionResult].
@ProviderFor(fusionResult)
const fusionResultProvider = FusionResultFamily();

/// See also [fusionResult].
class FusionResultFamily extends Family<AsyncValue<FusionResult>> {
  /// See also [fusionResult].
  const FusionResultFamily();

  /// See also [fusionResult].
  FusionResultProvider call(
    String storyId,
    double bias,
  ) {
    return FusionResultProvider(
      storyId,
      bias,
    );
  }

  @override
  FusionResultProvider getProviderOverride(
    covariant FusionResultProvider provider,
  ) {
    return call(
      provider.storyId,
      provider.bias,
    );
  }

  static const Iterable<ProviderOrFamily>? _dependencies = null;

  @override
  Iterable<ProviderOrFamily>? get dependencies => _dependencies;

  static const Iterable<ProviderOrFamily>? _allTransitiveDependencies = null;

  @override
  Iterable<ProviderOrFamily>? get allTransitiveDependencies =>
      _allTransitiveDependencies;

  @override
  String? get name => r'fusionResultProvider';
}

/// See also [fusionResult].
class FusionResultProvider extends AutoDisposeFutureProvider<FusionResult> {
  /// See also [fusionResult].
  FusionResultProvider(
    String storyId,
    double bias,
  ) : this._internal(
          (ref) => fusionResult(
            ref as FusionResultRef,
            storyId,
            bias,
          ),
          from: fusionResultProvider,
          name: r'fusionResultProvider',
          debugGetCreateSourceHash:
              const bool.fromEnvironment('dart.vm.product')
                  ? null
                  : _$fusionResultHash,
          dependencies: FusionResultFamily._dependencies,
          allTransitiveDependencies:
              FusionResultFamily._allTransitiveDependencies,
          storyId: storyId,
          bias: bias,
        );

  FusionResultProvider._internal(
    super._createNotifier, {
    required super.name,
    required super.dependencies,
    required super.allTransitiveDependencies,
    required super.debugGetCreateSourceHash,
    required super.from,
    required this.storyId,
    required this.bias,
  }) : super.internal();

  final String storyId;
  final double bias;

  @override
  Override overrideWith(
    FutureOr<FusionResult> Function(FusionResultRef provider) create,
  ) {
    return ProviderOverride(
      origin: this,
      override: FusionResultProvider._internal(
        (ref) => create(ref as FusionResultRef),
        from: from,
        name: null,
        dependencies: null,
        allTransitiveDependencies: null,
        debugGetCreateSourceHash: null,
        storyId: storyId,
        bias: bias,
      ),
    );
  }

  @override
  AutoDisposeFutureProviderElement<FusionResult> createElement() {
    return _FusionResultProviderElement(this);
  }

  @override
  bool operator ==(Object other) {
    return other is FusionResultProvider &&
        other.storyId == storyId &&
        other.bias == bias;
  }

  @override
  int get hashCode {
    var hash = _SystemHash.combine(0, runtimeType.hashCode);
    hash = _SystemHash.combine(hash, storyId.hashCode);
    hash = _SystemHash.combine(hash, bias.hashCode);

    return _SystemHash.finish(hash);
  }
}

@Deprecated('Will be removed in 3.0. Use Ref instead')
// ignore: unused_element
mixin FusionResultRef on AutoDisposeFutureProviderRef<FusionResult> {
  /// The parameter `storyId` of this provider.
  String get storyId;

  /// The parameter `bias` of this provider.
  double get bias;
}

class _FusionResultProviderElement
    extends AutoDisposeFutureProviderElement<FusionResult>
    with FusionResultRef {
  _FusionResultProviderElement(super.provider);

  @override
  String get storyId => (origin as FusionResultProvider).storyId;
  @override
  double get bias => (origin as FusionResultProvider).bias;
}

String _$timelineHash() => r'85c5c1760141f2f3f687ce875c39ccb6e4ee3d93';

/// See also [timeline].
@ProviderFor(timeline)
const timelineProvider = TimelineFamily();

/// See also [timeline].
class TimelineFamily extends Family<AsyncValue<List<TimelineChunk>>> {
  /// See also [timeline].
  const TimelineFamily();

  /// See also [timeline].
  TimelineProvider call(
    String storyId,
  ) {
    return TimelineProvider(
      storyId,
    );
  }

  @override
  TimelineProvider getProviderOverride(
    covariant TimelineProvider provider,
  ) {
    return call(
      provider.storyId,
    );
  }

  static const Iterable<ProviderOrFamily>? _dependencies = null;

  @override
  Iterable<ProviderOrFamily>? get dependencies => _dependencies;

  static const Iterable<ProviderOrFamily>? _allTransitiveDependencies = null;

  @override
  Iterable<ProviderOrFamily>? get allTransitiveDependencies =>
      _allTransitiveDependencies;

  @override
  String? get name => r'timelineProvider';
}

/// See also [timeline].
class TimelineProvider extends AutoDisposeFutureProvider<List<TimelineChunk>> {
  /// See also [timeline].
  TimelineProvider(
    String storyId,
  ) : this._internal(
          (ref) => timeline(
            ref as TimelineRef,
            storyId,
          ),
          from: timelineProvider,
          name: r'timelineProvider',
          debugGetCreateSourceHash:
              const bool.fromEnvironment('dart.vm.product')
                  ? null
                  : _$timelineHash,
          dependencies: TimelineFamily._dependencies,
          allTransitiveDependencies: TimelineFamily._allTransitiveDependencies,
          storyId: storyId,
        );

  TimelineProvider._internal(
    super._createNotifier, {
    required super.name,
    required super.dependencies,
    required super.allTransitiveDependencies,
    required super.debugGetCreateSourceHash,
    required super.from,
    required this.storyId,
  }) : super.internal();

  final String storyId;

  @override
  Override overrideWith(
    FutureOr<List<TimelineChunk>> Function(TimelineRef provider) create,
  ) {
    return ProviderOverride(
      origin: this,
      override: TimelineProvider._internal(
        (ref) => create(ref as TimelineRef),
        from: from,
        name: null,
        dependencies: null,
        allTransitiveDependencies: null,
        debugGetCreateSourceHash: null,
        storyId: storyId,
      ),
    );
  }

  @override
  AutoDisposeFutureProviderElement<List<TimelineChunk>> createElement() {
    return _TimelineProviderElement(this);
  }

  @override
  bool operator ==(Object other) {
    return other is TimelineProvider && other.storyId == storyId;
  }

  @override
  int get hashCode {
    var hash = _SystemHash.combine(0, runtimeType.hashCode);
    hash = _SystemHash.combine(hash, storyId.hashCode);

    return _SystemHash.finish(hash);
  }
}

@Deprecated('Will be removed in 3.0. Use Ref instead')
// ignore: unused_element
mixin TimelineRef on AutoDisposeFutureProviderRef<List<TimelineChunk>> {
  /// The parameter `storyId` of this provider.
  String get storyId;
}

class _TimelineProviderElement
    extends AutoDisposeFutureProviderElement<List<TimelineChunk>>
    with TimelineRef {
  _TimelineProviderElement(super.provider);

  @override
  String get storyId => (origin as TimelineProvider).storyId;
}

String _$storiesNotifierHash() => r'93d82ada90fb525c5ebe99d3cd1cfcb0e82ad69e';

/// See also [StoriesNotifier].
@ProviderFor(StoriesNotifier)
final storiesNotifierProvider =
    AutoDisposeAsyncNotifierProvider<StoriesNotifier, List<Story>>.internal(
  StoriesNotifier.new,
  name: r'storiesNotifierProvider',
  debugGetCreateSourceHash: const bool.fromEnvironment('dart.vm.product')
      ? null
      : _$storiesNotifierHash,
  dependencies: null,
  allTransitiveDependencies: null,
);

typedef _$StoriesNotifier = AutoDisposeAsyncNotifier<List<Story>>;
String _$searchNotifierHash() => r'66d3f55b668278648407fb52b3e71ea6ea2e6a4b';

/// See also [SearchNotifier].
@ProviderFor(SearchNotifier)
final searchNotifierProvider =
    AutoDisposeAsyncNotifierProvider<SearchNotifier, List<Story>?>.internal(
  SearchNotifier.new,
  name: r'searchNotifierProvider',
  debugGetCreateSourceHash: const bool.fromEnvironment('dart.vm.product')
      ? null
      : _$searchNotifierHash,
  dependencies: null,
  allTransitiveDependencies: null,
);

typedef _$SearchNotifier = AutoDisposeAsyncNotifier<List<Story>?>;
String _$chatNotifierHash() => r'f24ed217bfa67e8742a0a529dde63483d240828b';

abstract class _$ChatNotifier
    extends BuildlessAutoDisposeAsyncNotifier<List<ChatMessage>> {
  late final String storyId;

  FutureOr<List<ChatMessage>> build(
    String storyId,
  );
}

/// See also [ChatNotifier].
@ProviderFor(ChatNotifier)
const chatNotifierProvider = ChatNotifierFamily();

/// See also [ChatNotifier].
class ChatNotifierFamily extends Family<AsyncValue<List<ChatMessage>>> {
  /// See also [ChatNotifier].
  const ChatNotifierFamily();

  /// See also [ChatNotifier].
  ChatNotifierProvider call(
    String storyId,
  ) {
    return ChatNotifierProvider(
      storyId,
    );
  }

  @override
  ChatNotifierProvider getProviderOverride(
    covariant ChatNotifierProvider provider,
  ) {
    return call(
      provider.storyId,
    );
  }

  static const Iterable<ProviderOrFamily>? _dependencies = null;

  @override
  Iterable<ProviderOrFamily>? get dependencies => _dependencies;

  static const Iterable<ProviderOrFamily>? _allTransitiveDependencies = null;

  @override
  Iterable<ProviderOrFamily>? get allTransitiveDependencies =>
      _allTransitiveDependencies;

  @override
  String? get name => r'chatNotifierProvider';
}

/// See also [ChatNotifier].
class ChatNotifierProvider extends AutoDisposeAsyncNotifierProviderImpl<
    ChatNotifier, List<ChatMessage>> {
  /// See also [ChatNotifier].
  ChatNotifierProvider(
    String storyId,
  ) : this._internal(
          () => ChatNotifier()..storyId = storyId,
          from: chatNotifierProvider,
          name: r'chatNotifierProvider',
          debugGetCreateSourceHash:
              const bool.fromEnvironment('dart.vm.product')
                  ? null
                  : _$chatNotifierHash,
          dependencies: ChatNotifierFamily._dependencies,
          allTransitiveDependencies:
              ChatNotifierFamily._allTransitiveDependencies,
          storyId: storyId,
        );

  ChatNotifierProvider._internal(
    super._createNotifier, {
    required super.name,
    required super.dependencies,
    required super.allTransitiveDependencies,
    required super.debugGetCreateSourceHash,
    required super.from,
    required this.storyId,
  }) : super.internal();

  final String storyId;

  @override
  FutureOr<List<ChatMessage>> runNotifierBuild(
    covariant ChatNotifier notifier,
  ) {
    return notifier.build(
      storyId,
    );
  }

  @override
  Override overrideWith(ChatNotifier Function() create) {
    return ProviderOverride(
      origin: this,
      override: ChatNotifierProvider._internal(
        () => create()..storyId = storyId,
        from: from,
        name: null,
        dependencies: null,
        allTransitiveDependencies: null,
        debugGetCreateSourceHash: null,
        storyId: storyId,
      ),
    );
  }

  @override
  AutoDisposeAsyncNotifierProviderElement<ChatNotifier, List<ChatMessage>>
      createElement() {
    return _ChatNotifierProviderElement(this);
  }

  @override
  bool operator ==(Object other) {
    return other is ChatNotifierProvider && other.storyId == storyId;
  }

  @override
  int get hashCode {
    var hash = _SystemHash.combine(0, runtimeType.hashCode);
    hash = _SystemHash.combine(hash, storyId.hashCode);

    return _SystemHash.finish(hash);
  }
}

@Deprecated('Will be removed in 3.0. Use Ref instead')
// ignore: unused_element
mixin ChatNotifierRef
    on AutoDisposeAsyncNotifierProviderRef<List<ChatMessage>> {
  /// The parameter `storyId` of this provider.
  String get storyId;
}

class _ChatNotifierProviderElement
    extends AutoDisposeAsyncNotifierProviderElement<ChatNotifier,
        List<ChatMessage>> with ChatNotifierRef {
  _ChatNotifierProviderElement(super.provider);

  @override
  String get storyId => (origin as ChatNotifierProvider).storyId;
}
// ignore_for_file: type=lint
// ignore_for_file: subtype_of_sealed_class, invalid_use_of_internal_member, invalid_use_of_visible_for_testing_member, deprecated_member_use_from_same_package
