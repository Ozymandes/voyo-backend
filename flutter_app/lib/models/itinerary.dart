class Itinerary {
  final int id;
  final String userId;
  final String title;
  final int? regionId;
  final String status; // 'draft', 'current', 'completed'
  final DateTime? startDate;
  final DateTime? endDate;

  const Itinerary({
    required this.id,
    required this.userId,
    required this.title,
    this.regionId,
    required this.status,
    this.startDate,
    this.endDate,
  });

  factory Itinerary.fromJson(Map<String, dynamic> json) {
    return Itinerary(
      id: json['id'] as int,
      userId: json['user_id'] as String,
      title: json['title'] as String,
      regionId: json['region_id'] as int?,
      status: json['status'] as String,
      startDate: json['start_date'] != null
          ? DateTime.parse(json['start_date'] as String)
          : null,
      endDate: json['end_date'] != null
          ? DateTime.parse(json['end_date'] as String)
          : null,
    );
  }
}

class ItineraryItem {
  final int id;
  final int itineraryId;
  final int? poiId;
  final int dayNumber;
  final int sequenceOrder;
  final String startTime;
  final String? endTime;
  final String? customTitle;
  final String? customDescription;

  const ItineraryItem({
    required this.id,
    required this.itineraryId,
    this.poiId,
    required this.dayNumber,
    required this.sequenceOrder,
    required this.startTime,
    this.endTime,
    this.customTitle,
    this.customDescription,
  });

  factory ItineraryItem.fromJson(Map<String, dynamic> json) {
    return ItineraryItem(
      id: json['id'] as int,
      itineraryId: json['itinerary_id'] as int,
      poiId: json['poi_id'] as int?,
      dayNumber: json['day_number'] as int,
      sequenceOrder: json['sequence_order'] as int,
      startTime: json['start_time'] as String,
      endTime: json['end_time'] as String?,
      customTitle: json['custom_title'] as String?,
      customDescription: json['custom_description'] as String?,
    );
  }
}
