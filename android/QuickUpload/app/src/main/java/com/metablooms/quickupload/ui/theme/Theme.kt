package com.metablooms.quickupload.ui.theme

import android.os.Build
import androidx.compose.foundation.isSystemInDarkTheme
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.darkColorScheme
import androidx.compose.material3.dynamicDarkColorScheme
import androidx.compose.material3.dynamicLightColorScheme
import androidx.compose.material3.lightColorScheme
import androidx.compose.runtime.Composable
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.platform.LocalContext

private val DarkColorScheme = darkColorScheme(
    primary = Color(0xFF58A6FF),
    secondary = Color(0xFF3FB950),
    tertiary = Color(0xFFD2A8FF),
    background = Color(0xFF0D1117),
    surface = Color(0xFF161B22),
    onPrimary = Color.White,
    onSecondary = Color.White,
    onBackground = Color(0xFFC9D1D9),
    onSurface = Color(0xFFC9D1D9),
    error = Color(0xFFF85149)
)

private val LightColorScheme = lightColorScheme(
    primary = Color(0xFF0969DA),
    secondary = Color(0xFF1A7F37),
    tertiary = Color(0xFF8250DF),
    background = Color(0xFFFFFFFF),
    surface = Color(0xFFF6F8FA),
    onPrimary = Color.White,
    onSecondary = Color.White,
    onBackground = Color(0xFF1F2328),
    onSurface = Color(0xFF1F2328),
    error = Color(0xFFCF222E)
)

@Composable
fun QuickUploadTheme(
    darkTheme: Boolean = isSystemInDarkTheme(),
    dynamicColor: Boolean = true,
    content: @Composable () -> Unit
) {
    val colorScheme = when {
        dynamicColor && Build.VERSION.SDK_INT >= Build.VERSION_CODES.S -> {
            val context = LocalContext.current
            if (darkTheme) dynamicDarkColorScheme(context) else dynamicLightColorScheme(context)
        }
        darkTheme -> DarkColorScheme
        else -> LightColorScheme
    }

    MaterialTheme(
        colorScheme = colorScheme,
        content = content
    )
}
