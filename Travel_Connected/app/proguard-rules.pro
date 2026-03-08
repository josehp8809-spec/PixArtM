# ProGuard rules para Travlytic

# Keep Hilt
-keepclassmembers class * {
    @dagger.hilt.* <methods>;
    @javax.inject.* <methods>;
}

# Keep Room entities
-keep class com.travlytic.app.data.db.entities.** { *; }

# Keep Gson serialization
-keep class com.google.gson.** { *; }
-keepattributes Signature
-keepattributes *Annotation*

# Keep Google API models
-keep class com.google.api.services.sheets.** { *; }
-keep class com.google.api.client.** { *; }

# Keep Gemini SDK
-keep class com.google.ai.client.generativeai.** { *; }

# Keep Kotlin coroutines
-keepclassmembernames class kotlinx.** {
    volatile <fields>;
}
