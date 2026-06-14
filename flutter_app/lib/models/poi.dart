class Poi {
  final int id;
  final String name;
  final double latitude;
  final double longitude;
  final String? category;
  final double? averageRating;
  final int? totalReviews;
  final String? description;
  final double? ticketPrice;
  final String? currency;
  final Map<String, dynamic>? openingHours;
  final String? phoneNumber;
  final String? websiteUrl;
  final String? historicalSignificance;
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
    this.ticketPrice,
    this.currency,
    this.openingHours,
    this.phoneNumber,
    this.websiteUrl,
    this.historicalSignificance,
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
      ticketPrice: json['ticket_price'] != null
          ? (json['ticket_price'] as num).toDouble()
          : null,
      currency: json['currency'] as String?,
      openingHours: json['opening_hours'] as Map<String, dynamic>?,
      phoneNumber: json['phone_number'] as String?,
      websiteUrl: json['website_url'] as String?,
      historicalSignificance: json['historical_significance'] as String?,
      isVerified: json['is_verified'] as bool? ?? false,
      popularityScore: json['popularity_score'] != null
          ? (json['popularity_score'] as num).toDouble()
          : null,
      city: json['city'] as String?,
      averageVisitDuration: json['average_visit_duration'] as int?,
      imageUrls: (json['image_urls'] as List<dynamic>?)
          ?.map((e) => e as String)
          .toList(),
      tags: (json['tags'] as List<dynamic>?)?.map((e) => e as String).toList(),
      address: json['address'] as String?,
    );
  }
}
