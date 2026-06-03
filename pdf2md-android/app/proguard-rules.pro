# MuPDF — native JNI bridge, niet strippen
-keep class com.artifex.mupdf.** { *; }
-dontwarn com.artifex.mupdf.**

# ML Kit — reflectie intern gebruikt
-keep class com.google.mlkit.** { *; }
-dontwarn com.google.mlkit.**

# Kotlin coroutines
-keepnames class kotlinx.coroutines.internal.MainDispatcherFactory {}
-keepnames class kotlinx.coroutines.CoroutineExceptionHandler {}
