package com.travlytic.app.ui.screens

import androidx.compose.foundation.layout.*
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.filled.ArrowBack
import androidx.compose.material3.*
import androidx.compose.runtime.Composable
import androidx.compose.runtime.collectAsState
import androidx.compose.runtime.getValue
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import androidx.hilt.navigation.compose.hiltViewModel
import com.travlytic.app.ui.theme.*
import com.travlytic.app.ui.viewmodel.MainViewModel

@OptIn(ExperimentalMaterial3Api::class)
@Composable
fun ChannelsScreen(
    viewModel: MainViewModel = hiltViewModel(),
    onNavigateBack: () -> Unit
) {
    val wpEnabled by viewModel.channelWhatsApp.collectAsState()
    val fbEnabled by viewModel.channelFbMessenger.collectAsState()
    val igEnabled by viewModel.channelIgDirect.collectAsState()

    Scaffold(
        containerColor = TravlyticSurface,
        topBar = {
            TopAppBar(
                title = { Text("Canales IA", color = TravlyticOnSurface, fontWeight = FontWeight.SemiBold) },
                navigationIcon = {
                    IconButton(onClick = onNavigateBack) {
                        Icon(Icons.Filled.ArrowBack, "Volver", tint = TravlyticOnSurface)
                    }
                },
                colors = TopAppBarDefaults.topAppBarColors(containerColor = TravlyticSurface)
            )
        }
    ) { padding ->
        Column(
            modifier = Modifier
                .fillMaxSize()
                .padding(padding)
                .padding(16.dp),
            verticalArrangement = Arrangement.spacedBy(16.dp)
        ) {
            Text(
                "Selecciona en qué aplicaciones deseas que la IA intercepte notificaciones de CHAT para responder automáticamente. Los Estados e Historias serán ignorados.",
                color = TravlyticOnSurface2, fontSize = 13.sp, lineHeight = 18.sp
            )
            
            Spacer(Modifier.height(8.dp))

            ChannelCard(
                name = "WhatsApp & WhatsApp Business",
                description = "Paquete: com.whatsapp",
                icon = "💬",
                isEnabled = wpEnabled,
                onToggle = { viewModel.toggleChannelWhatsApp(it) }
            )

            ChannelCard(
                name = "Facebook Messenger",
                description = "Paquete: com.facebook.orca",
                icon = "🔵",
                isEnabled = fbEnabled,
                onToggle = { viewModel.toggleChannelFbMessenger(it) }
            )

            ChannelCard(
                name = "Instagram Direct",
                description = "Paquete: com.instagram.android",
                icon = "📸",
                isEnabled = igEnabled,
                onToggle = { viewModel.toggleChannelIgDirect(it) }
            )
        }
    }
}

@Composable
fun ChannelCard(
    name: String,
    description: String,
    icon: String,
    isEnabled: Boolean,
    onToggle: (Boolean) -> Unit
) {
    Card(
        modifier = Modifier.fillMaxWidth(),
        colors = CardDefaults.cardColors(containerColor = TravlyticSurface2),
        shape = RoundedCornerShape(12.dp)
    ) {
        Row(
            modifier = Modifier.padding(16.dp).fillMaxWidth(),
            verticalAlignment = Alignment.CenterVertically
        ) {
            Text(icon, fontSize = 24.sp)
            Spacer(Modifier.width(16.dp))
            Column(Modifier.weight(1f)) {
                Text(name, color = TravlyticOnSurface, fontWeight = FontWeight.SemiBold, fontSize = 15.sp)
                Text(description, color = TravlyticOnSurface2, fontSize = 11.sp)
            }
            Switch(
                checked = isEnabled,
                onCheckedChange = onToggle,
                colors = SwitchDefaults.colors(
                    checkedThumbColor = Color.White,
                    checkedTrackColor = TravlyticGreen,
                    uncheckedThumbColor = TravlyticOnSurface2,
                    uncheckedTrackColor = TravlyticSurface3
                )
            )
        }
    }
}
