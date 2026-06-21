class Poi {
  final int id;
  final String name;
  final double latitude;
  final double longitude;
  final String? category;
  final double? averageRating;
  final int? totalReviews;
  final String? description;
  final String? narrative;
  final double? ticketPrice;
  final String? currency;
  final Map<String, dynamic>? ticketPrices;
  final Map<String, dynamic>? openingHours;
  final String? phoneNumber;
  final String? websiteUrl;
  final String? historicalSignificance;
  final List<String>? travelTips; // expert guidance from enrichment (feeds "Good to know" card)
  final bool isVerified;
  final double? popularityScore;
  final String? city;
  final int? averageVisitDuration; // minutes
  final List<String>? imageUrls;
  final List<String>? tags;
  final String? address;

  Poi({
    required this.id,
    required this.name,
    required this.latitude,
    required this.longitude,
    this.category,
    this.averageRating,
    this.totalReviews,
    this.description,
    this.narrative,
    this.ticketPrice,
    this.currency,
    this.ticketPrices,
    this.openingHours,
    this.phoneNumber,
    this.websiteUrl,
    this.historicalSignificance,
    this.travelTips,
    this.isVerified = false,
    this.popularityScore,
    this.city,
    this.averageVisitDuration,
    this.imageUrls,
    this.tags,
    this.address,
  });

  /// Hidden gem: low popularity but verified quality
  bool get isHiddenGem =>
      isVerified && popularityScore != null && popularityScore! < 30;

  /// Normalize a JSON value that should be a list of strings into one.
  /// Accepts: List<dynamic>, Map wrapping a list under [unwrapKey]
  /// (the legacy {key:[...]} shape some seed rows carried), null, or a single
  /// value. Never throws — returns null for anything unusable. The Explore
  /// 'DB error: _Map is not a subtype of List' crash came from the Map case.
  static List<String>? _stringList(dynamic v, {String? unwrapKey}) {
    dynamic src = v;
    if (src is Map && unwrapKey != null) {
      src = src[unwrapKey];
    }
    if (src == null) return null;
    if (src is! List) return null;
    return src
        .whereType<String>()
        .where((s) => s.trim().isNotEmpty)
        .toList(growable: false);
  }

  factory Poi.fromJson(Map<String, dynamic> json) {
    return Poi(
      id: json['id'] as int,
      name: json['name'] as String,
      latitude: (json['latitude'] as num).toDouble(),
      longitude: (json['longitude'] as num).toDouble(),
      category: json['category'] as String?,
      averageRating: json['average_rating'] != null
          ? (json['average_rating'] as num).toDouble()
          : null,
      totalReviews: json['total_reviews'] as int?,
      description: json['description'] as String?,
      narrative: json['narrative'] as String?,
      ticketPrice: json['ticket_price'] != null
          ? (json['ticket_price'] as num).toDouble()
          : null,
      currency: json['currency'] as String?,
      ticketPrices: json['ticket_prices'] is Map<String, dynamic>
          ? json['ticket_prices'] as Map<String, dynamic>
          : null,
      openingHours: json['opening_hours'] is Map<String, dynamic>
          ? json['opening_hours'] as Map<String, dynamic>
          : null,
      phoneNumber: json['phone_number'] as String?,
      websiteUrl: json['website_url'] as String?,
      historicalSignificance: json['historical_significance'] as String?,
      travelTips: _stringList(json['travel_tips']),
      isVerified: json['is_verified'] as bool? ?? false,
      popularityScore: json['popularity_score'] != null
          ? (json['popularity_score'] as num).toDouble()
          : null,
      city: json['city'] as String?,
      averageVisitDuration: json['average_visit_duration'] as int?,
      imageUrls: _stringList(json['image_urls'], unwrapKey: 'images'),
      tags: _stringList(json['tags'], unwrapKey: 'tags'),
      address: json['address'] as String?,
    );
  }
}
