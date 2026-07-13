package com.ddakpul.math.ui

import androidx.compose.foundation.layout.Row
import androidx.compose.foundation.layout.fillMaxSize
import androidx.compose.foundation.layout.padding
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.automirrored.filled.MenuBook
import androidx.compose.material.icons.filled.BarChart
import androidx.compose.material.icons.filled.Home
import androidx.compose.material.icons.filled.Settings
import androidx.compose.material3.Icon
import androidx.compose.material3.NavigationBar
import androidx.compose.material3.NavigationBarItem
import androidx.compose.material3.NavigationRail
import androidx.compose.material3.NavigationRailItem
import androidx.compose.material3.Scaffold
import androidx.compose.material3.Text
import androidx.compose.material3.windowsizeclass.WindowSizeClass
import androidx.compose.material3.windowsizeclass.WindowWidthSizeClass
import androidx.compose.runtime.Composable
import androidx.compose.runtime.getValue
import androidx.compose.ui.Modifier
import androidx.compose.ui.graphics.vector.ImageVector
import androidx.compose.ui.res.stringResource
import androidx.navigation.NavGraph.Companion.findStartDestination
import androidx.navigation.NavHostController
import androidx.navigation.compose.NavHost
import androidx.navigation.compose.composable
import androidx.navigation.compose.currentBackStackEntryAsState
import androidx.navigation.compose.rememberNavController
import com.ddakpul.math.R
import com.ddakpul.math.presentation.home.HomeScreen
import com.ddakpul.math.presentation.paywall.PaywallScreen
import com.ddakpul.math.presentation.print.PrintScreen
import com.ddakpul.math.presentation.privacy.PrivacyScreen
import com.ddakpul.math.presentation.report.ReportScreen
import com.ddakpul.math.presentation.settings.SettingsScreen
import com.ddakpul.math.presentation.solve.SolveScreen

private enum class DdakPulDestination(
    val route: String,
    val labelRes: Int,
    val icon: ImageVector,
) {
    HOME("home", R.string.nav_home, Icons.Filled.Home),
    SOLVE("solve", R.string.nav_solve, Icons.AutoMirrored.Filled.MenuBook),
    REPORT("report", R.string.nav_report, Icons.Filled.BarChart),
    SETTINGS("settings", R.string.nav_settings, Icons.Filled.Settings),
}

/** 탭이 아닌 보조 화면 라우트. */
private const val PRINT_ROUTE = "print"
private const val PAYWALL_ROUTE = "paywall"
private const val PRIVACY_ROUTE = "privacy"

@Composable
fun DdakPulApp(
    windowSizeClass: WindowSizeClass,
    modifier: Modifier = Modifier,
) {
    val navController = rememberNavController()
    // 태블릿(가로 폭이 Compact보다 크면) 사이드 레일, 폰이면 하단 바.
    val useRail = windowSizeClass.widthSizeClass != WindowWidthSizeClass.Compact

    if (useRail) {
        Row(modifier = modifier.fillMaxSize()) {
            DdakPulNavigationRail(navController)
            AppNavHost(navController = navController, modifier = Modifier.fillMaxSize())
        }
    } else {
        Scaffold(
            modifier = modifier.fillMaxSize(),
            bottomBar = { DdakPulBottomBar(navController) },
        ) { innerPadding ->
            AppNavHost(navController = navController, modifier = Modifier.padding(innerPadding))
        }
    }
}

@Composable
private fun AppNavHost(
    navController: NavHostController,
    modifier: Modifier = Modifier,
) {
    NavHost(
        navController = navController,
        startDestination = DdakPulDestination.HOME.route,
        modifier = modifier,
    ) {
        composable(DdakPulDestination.HOME.route) {
            HomeScreen(onStartLearning = { navController.switchTab(DdakPulDestination.SOLVE.route) })
        }
        composable(DdakPulDestination.SOLVE.route) {
            SolveScreen(
                onGoHome = { navController.switchTab(DdakPulDestination.HOME.route) },
                onUpgrade = { navController.navigate(PAYWALL_ROUTE) },
            )
        }
        composable(DdakPulDestination.REPORT.route) {
            ReportScreen(
                onPrintClick = { navController.navigate(PRINT_ROUTE) },
                onOpenPaywall = { navController.navigate(PAYWALL_ROUTE) },
            )
        }
        composable(DdakPulDestination.SETTINGS.route) {
            SettingsScreen(
                onOpenPaywall = { navController.navigate(PAYWALL_ROUTE) },
                onOpenPrivacy = { navController.navigate(PRIVACY_ROUTE) },
            )
        }
        composable(PRINT_ROUTE) { PrintScreen(onBack = { navController.popBackStack() }) }
        composable(PAYWALL_ROUTE) { PaywallScreen(onClose = { navController.popBackStack() }) }
        composable(PRIVACY_ROUTE) { PrivacyScreen(onBack = { navController.popBackStack() }) }
    }
}

@Composable
private fun DdakPulBottomBar(navController: NavHostController) {
    val currentRoute = navController.currentRoute()
    NavigationBar {
        DdakPulDestination.entries.forEach { destination ->
            NavigationBarItem(
                selected = currentRoute == destination.route,
                onClick = { navController.switchTab(destination.route) },
                icon = { Icon(destination.icon, contentDescription = stringResource(destination.labelRes)) },
                label = { Text(stringResource(destination.labelRes)) },
            )
        }
    }
}

@Composable
private fun DdakPulNavigationRail(navController: NavHostController) {
    val currentRoute = navController.currentRoute()
    NavigationRail {
        DdakPulDestination.entries.forEach { destination ->
            NavigationRailItem(
                selected = currentRoute == destination.route,
                onClick = { navController.switchTab(destination.route) },
                icon = { Icon(destination.icon, contentDescription = stringResource(destination.labelRes)) },
                label = { Text(stringResource(destination.labelRes)) },
            )
        }
    }
}

@Composable
private fun NavHostController.currentRoute(): String? = currentBackStackEntryAsState().value?.destination?.route

/** 탭 전환 — 시작 목적지까지 팝업하며 상태를 저장/복원해 탭 간 이동을 자연스럽게 한다. */
private fun NavHostController.switchTab(route: String) {
    navigate(route) {
        popUpTo(graph.findStartDestination().id) { saveState = true }
        launchSingleTop = true
        restoreState = true
    }
}
