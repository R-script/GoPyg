package com.example.gopygapp.ui.theme

import android.os.Build
import androidx.compose.foundation.isSystemInDarkTheme
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.darkColorScheme
import androidx.compose.material3.dynamicDarkColorScheme
import androidx.compose.material3.dynamicLightColorScheme
import androidx.compose.material3.lightColorScheme
import androidx.compose.runtime.Composable
import androidx.compose.ui.platform.LocalContext

// Define your custom colors here
private val DarkColorScheme = darkColorScheme(
    primary = Purple80,
    secondary = PurpleGrey80,
    tertiary = Pink80
)

private val LightColorScheme = lightColorScheme(
    primary = Purple40,
    secondary = PurpleGrey40,
    tertiary = Pink40
)

@Composable
fun Gopyg11Theme(
    darkTheme: Boolean = isSystemInDarkTheme(), // Checks if the system is using dark theme
    dynamicColor: Boolean = true, // Enables dynamic color (works only on Android 12+)
    content: @Composable () -> Unit
) {
    val context = LocalContext.current
    val colorScheme = when {
        dynamicColor && Build.VERSION.SDK_INT >= Build.VERSION_CODES.S -> {
            // Use dynamic color schemes if the Android version is 12 or higher
            if (darkTheme) dynamicDarkColorScheme(context) else dynamicLightColorScheme(context)
        }
        darkTheme -> DarkColorScheme // Use the predefined dark color scheme
        else -> LightColorScheme // Use the predefined light color scheme
    }

    MaterialTheme(
        colorScheme = colorScheme, // Pass the appropriate color scheme
        typography = Typography, // You should have a Typography object defined elsewhere
        content = content // Content composable that uses this theme
    )
}
