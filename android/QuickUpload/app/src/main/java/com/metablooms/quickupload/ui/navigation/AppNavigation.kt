package com.metablooms.quickupload.ui.navigation

import androidx.compose.foundation.layout.padding
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.filled.*
import androidx.compose.material3.*
import androidx.compose.runtime.*
import androidx.compose.ui.Modifier
import androidx.compose.ui.graphics.vector.ImageVector
import androidx.lifecycle.compose.collectAsStateWithLifecycle
import androidx.lifecycle.viewmodel.compose.viewModel
import androidx.navigation.NavDestination.Companion.hierarchy
import androidx.navigation.NavGraph.Companion.findStartDestination
import androidx.navigation.compose.NavHost
import androidx.navigation.compose.composable
import androidx.navigation.compose.currentBackStackEntryAsState
import androidx.navigation.compose.rememberNavController
import com.metablooms.quickupload.ui.screens.AuthScreen
import com.metablooms.quickupload.ui.screens.HomeScreen
import com.metablooms.quickupload.ui.screens.QueueScreen
import com.metablooms.quickupload.ui.screens.SettingsScreen
import com.metablooms.quickupload.viewmodel.AuthViewModel
import com.metablooms.quickupload.viewmodel.HomeViewModel
import com.metablooms.quickupload.viewmodel.QueueViewModel

enum class Screen(val route: String, val label: String, val icon: ImageVector) {
    HOME("home", "Upload", Icons.Default.CloudUpload),
    QUEUE("queue", "Queue", Icons.Default.List),
    AUTH("auth", "Account", Icons.Default.AccountCircle),
    SETTINGS("settings", "Settings", Icons.Default.Settings)
}

@OptIn(ExperimentalMaterial3Api::class)
@Composable
fun AppNavigation() {
    val navController = rememberNavController()
    val authViewModel: AuthViewModel = viewModel()
    val homeViewModel: HomeViewModel = viewModel()
    val queueViewModel: QueueViewModel = viewModel()

    val authState by authViewModel.uiState.collectAsStateWithLifecycle()
    val homeState by homeViewModel.uiState.collectAsStateWithLifecycle()
    val queueItems by queueViewModel.items.collectAsStateWithLifecycle()

    val bottomBarScreens = listOf(Screen.HOME, Screen.QUEUE, Screen.SETTINGS)

    Scaffold(
        topBar = {
            TopAppBar(
                title = { Text("QuickUpload") }
            )
        },
        bottomBar = {
            NavigationBar {
                val navBackStackEntry by navController.currentBackStackEntryAsState()
                val currentDestination = navBackStackEntry?.destination

                bottomBarScreens.forEach { screen ->
                    NavigationBarItem(
                        icon = {
                            if (screen == Screen.QUEUE && queueItems.any {
                                    it.status.name == "UPLOADING" || it.status.name == "QUEUED"
                                }) {
                                BadgedBox(badge = {
                                    Badge {
                                        Text(
                                            queueItems.count {
                                                it.status.name == "UPLOADING" || it.status.name == "QUEUED"
                                            }.toString()
                                        )
                                    }
                                }) {
                                    Icon(screen.icon, contentDescription = screen.label)
                                }
                            } else {
                                Icon(screen.icon, contentDescription = screen.label)
                            }
                        },
                        label = { Text(screen.label) },
                        selected = currentDestination?.hierarchy?.any { it.route == screen.route } == true,
                        onClick = {
                            navController.navigate(screen.route) {
                                popUpTo(navController.graph.findStartDestination().id) {
                                    saveState = true
                                }
                                launchSingleTop = true
                                restoreState = true
                            }
                        }
                    )
                }
            }
        }
    ) { innerPadding ->
        NavHost(
            navController = navController,
            startDestination = Screen.HOME.route,
            modifier = Modifier.padding(innerPadding)
        ) {
            composable(Screen.HOME.route) {
                HomeScreen(
                    uiState = homeState,
                    isLoggedIn = authState.isLoggedIn,
                    onNavigateToAuth = { navController.navigate(Screen.AUTH.route) },
                    onLoadRepos = homeViewModel::loadRepos,
                    onSelectRepo = homeViewModel::selectRepo,
                    onFilesSelected = homeViewModel::setSelectedFiles,
                    onCommitMessageChanged = homeViewModel::setCommitMessage,
                    onUpload = homeViewModel::enqueueUpload,
                    onClearError = homeViewModel::clearError
                )
            }

            composable(Screen.QUEUE.route) {
                QueueScreen(
                    items = queueItems,
                    onRetry = queueViewModel::retryItem,
                    onRemove = queueViewModel::removeItem,
                    onClearCompleted = queueViewModel::clearCompleted
                )
            }

            composable(Screen.AUTH.route) {
                AuthScreen(
                    uiState = authState,
                    onStartDeviceFlow = authViewModel::startDeviceFlow,
                    onLoginWithPat = authViewModel::loginWithPat,
                    onLogout = authViewModel::logout
                )
            }

            composable(Screen.SETTINGS.route) {
                SettingsScreen(
                    username = authState.username,
                    onLogout = authViewModel::logout,
                    onNavigateToAuth = { navController.navigate(Screen.AUTH.route) }
                )
            }
        }
    }
}
