class ItineraryPoi {
  final int poiId;
  final String name;
  final double latitude;
  final double longitude;
  final String? category;
  final int dayNumber;
  final int sequenceOrder;
  final int itemId;

  const ItineraryPoi({
    required this.poiId,
    required this.name,
    required this.latitude,
    required this.longitude,
    this.category,
    required this.dayNumber,
    required this.sequenceOrder,
    required this.itemId,
  });

  factory ItineraryPoi.fromJson(Map<String, dynamic> json) {
    return ItineraryPoi(
      poiId: json['poi_id'] as int,
      name: json['name'] as String,
      latitude: (json['latitude'] as num).toDouble(),
      longitude: (json['longitude'] as num).toDouble(),
      category: json['category'] as String?,
      dayNumber: json['day_number'] as int,
      sequenceOrder: json['sequence_order'] as int,
      itemId: json['item_id'] as int,
    );
  }
}
