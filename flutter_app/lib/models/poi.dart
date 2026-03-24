class Poi {
  final int id;
  final String name;
  final double latitude;
  final double longitude;
  final String? category;
  final double? averageRating;
  final String? description;

  Poi({
    required this.id,
    required this.name,
    required this.latitude,
    required this.longitude,
    this.category,
    this.averageRating,
    this.description,
  });

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
      description: json['description'] as String?,
    );
  }
}
