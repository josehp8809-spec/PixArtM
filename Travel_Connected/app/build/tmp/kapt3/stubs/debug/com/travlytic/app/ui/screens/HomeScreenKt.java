package com.travlytic.app.ui.screens;

@kotlin.Metadata(mv = {1, 9, 0}, k = 2, xi = 48, d1 = {"\u0000L\n\u0000\n\u0002\u0010\u0002\n\u0000\n\u0002\u0010\u000b\n\u0002\b\u0002\n\u0002\u0018\u0002\n\u0000\n\u0002\u0018\u0002\n\u0002\b\u0002\n\u0002\u0018\u0002\n\u0002\b\u0003\n\u0002\u0010\u000e\n\u0002\b\u0004\n\u0002\u0018\u0002\n\u0002\b\u0003\n\u0002\u0018\u0002\n\u0002\b\u0004\n\u0002\u0018\u0002\n\u0000\n\u0002\u0018\u0002\n\u0002\b\u0003\u001a:\u0010\u0000\u001a\u00020\u00012\u0006\u0010\u0002\u001a\u00020\u00032\u0006\u0010\u0004\u001a\u00020\u00032\u0012\u0010\u0005\u001a\u000e\u0012\u0004\u0012\u00020\u0003\u0012\u0004\u0012\u00020\u00010\u00062\f\u0010\u0007\u001a\b\u0012\u0004\u0012\u00020\u00010\bH\u0007\u001a\u0010\u0010\t\u001a\u00020\u00012\u0006\u0010\n\u001a\u00020\u000bH\u0007\u001a\b\u0010\f\u001a\u00020\u0001H\u0003\u001a \u0010\r\u001a\u00020\u00012\u0006\u0010\u000e\u001a\u00020\u000f2\u0006\u0010\u0010\u001a\u00020\u000f2\u0006\u0010\u0011\u001a\u00020\u000fH\u0003\u001a$\u0010\u0012\u001a\u00020\u00012\u0006\u0010\u0013\u001a\u00020\u00142\u0012\u0010\u0015\u001a\u000e\u0012\u0004\u0012\u00020\u0014\u0012\u0004\u0012\u00020\u00010\u0006H\u0007\u001a<\u0010\u0016\u001a\u00020\u00012\b\b\u0002\u0010\u0017\u001a\u00020\u00182\f\u0010\u0019\u001a\b\u0012\u0004\u0012\u00020\u00010\b2\f\u0010\u001a\u001a\b\u0012\u0004\u0012\u00020\u00010\b2\f\u0010\u001b\u001a\b\u0012\u0004\u0012\u00020\u00010\bH\u0007\u001a\u0010\u0010\u001c\u001a\u00020\u00012\u0006\u0010\u0013\u001a\u00020\u001dH\u0007\u001a2\u0010\u001e\u001a\u00020\u00012\u0006\u0010\n\u001a\u00020\u001f2\u0012\u0010 \u001a\u000e\u0012\u0004\u0012\u00020\u000f\u0012\u0004\u0012\u00020\u00010\u00062\f\u0010!\u001a\b\u0012\u0004\u0012\u00020\u00010\bH\u0007\u00a8\u0006\""}, d2 = {"BotStatusCard", "", "isServiceEnabled", "", "isListenerEnabled", "onToggle", "Lkotlin/Function1;", "onOpenSettings", "Lkotlin/Function0;", "DashboardCard", "state", "Lcom/travlytic/app/ui/viewmodel/DashboardState;", "DashboardDivider", "DashboardStat", "icon", "", "value", "label", "EscalationCard", "log", "Lcom/travlytic/app/data/db/entities/EscalationLog;", "onResolve", "HomeScreen", "viewModel", "Lcom/travlytic/app/ui/viewmodel/MainViewModel;", "onNavigateToSettings", "onNavigateToSchedule", "onNavigateToSummary", "ResponseLogCard", "Lcom/travlytic/app/data/db/entities/ResponseLog;", "TestMessageCard", "Lcom/travlytic/app/ui/viewmodel/TestMessageState;", "onSend", "onClear", "app_debug"})
public final class HomeScreenKt {
    
    @kotlin.OptIn(markerClass = {androidx.compose.material3.ExperimentalMaterial3Api.class})
    @androidx.compose.runtime.Composable()
    public static final void HomeScreen(@org.jetbrains.annotations.NotNull()
    com.travlytic.app.ui.viewmodel.MainViewModel viewModel, @org.jetbrains.annotations.NotNull()
    kotlin.jvm.functions.Function0<kotlin.Unit> onNavigateToSettings, @org.jetbrains.annotations.NotNull()
    kotlin.jvm.functions.Function0<kotlin.Unit> onNavigateToSchedule, @org.jetbrains.annotations.NotNull()
    kotlin.jvm.functions.Function0<kotlin.Unit> onNavigateToSummary) {
    }
    
    @androidx.compose.runtime.Composable()
    public static final void BotStatusCard(boolean isServiceEnabled, boolean isListenerEnabled, @org.jetbrains.annotations.NotNull()
    kotlin.jvm.functions.Function1<? super java.lang.Boolean, kotlin.Unit> onToggle, @org.jetbrains.annotations.NotNull()
    kotlin.jvm.functions.Function0<kotlin.Unit> onOpenSettings) {
    }
    
    @androidx.compose.runtime.Composable()
    public static final void ResponseLogCard(@org.jetbrains.annotations.NotNull()
    com.travlytic.app.data.db.entities.ResponseLog log) {
    }
    
    @androidx.compose.runtime.Composable()
    public static final void DashboardCard(@org.jetbrains.annotations.NotNull()
    com.travlytic.app.ui.viewmodel.DashboardState state) {
    }
    
    @androidx.compose.runtime.Composable()
    private static final void DashboardStat(java.lang.String icon, java.lang.String value, java.lang.String label) {
    }
    
    @androidx.compose.runtime.Composable()
    private static final void DashboardDivider() {
    }
    
    @androidx.compose.runtime.Composable()
    public static final void TestMessageCard(@org.jetbrains.annotations.NotNull()
    com.travlytic.app.ui.viewmodel.TestMessageState state, @org.jetbrains.annotations.NotNull()
    kotlin.jvm.functions.Function1<? super java.lang.String, kotlin.Unit> onSend, @org.jetbrains.annotations.NotNull()
    kotlin.jvm.functions.Function0<kotlin.Unit> onClear) {
    }
    
    @androidx.compose.runtime.Composable()
    public static final void EscalationCard(@org.jetbrains.annotations.NotNull()
    com.travlytic.app.data.db.entities.EscalationLog log, @org.jetbrains.annotations.NotNull()
    kotlin.jvm.functions.Function1<? super com.travlytic.app.data.db.entities.EscalationLog, kotlin.Unit> onResolve) {
    }
}