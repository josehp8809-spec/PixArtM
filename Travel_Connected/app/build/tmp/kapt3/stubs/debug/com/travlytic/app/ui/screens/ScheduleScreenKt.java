package com.travlytic.app.ui.screens;

@kotlin.Metadata(mv = {1, 9, 0}, k = 2, xi = 48, d1 = {"\u0000H\n\u0000\n\u0002\u0010\u0002\n\u0000\n\u0002\u0010\u000b\n\u0000\n\u0002\u0018\u0002\n\u0002\u0018\u0002\n\u0002\b\u0002\n\u0002\u0010\u000e\n\u0002\b\u0004\n\u0002\u0018\u0002\n\u0002\b\u0003\n\u0002\u0010\b\n\u0002\b\u0002\n\u0002\u0018\u0002\n\u0000\n\u0002\u0018\u0002\n\u0002\b\u0002\n\u0002\u0018\u0002\n\u0002\b\u0006\u001a#\u0010\u0000\u001a\u00020\u00012\u0006\u0010\u0002\u001a\u00020\u00032\u0011\u0010\u0004\u001a\r\u0012\u0004\u0012\u00020\u00010\u0005\u00a2\u0006\u0002\b\u0006H\u0003\u001a&\u0010\u0007\u001a\u00020\u00012\u0006\u0010\b\u001a\u00020\t2\u0006\u0010\n\u001a\u00020\u00032\f\u0010\u000b\u001a\b\u0012\u0004\u0012\u00020\u00010\u0005H\u0007\u001a \u0010\f\u001a\u00020\u00012\b\b\u0002\u0010\r\u001a\u00020\u000e2\f\u0010\u000f\u001a\b\u0012\u0004\u0012\u00020\u00010\u0005H\u0007\u001aB\u0010\u0010\u001a\u00020\u00012\u0006\u0010\b\u001a\u00020\t2\u0006\u0010\u0011\u001a\u00020\u00122\u0006\u0010\u0013\u001a\u00020\u00122\u0006\u0010\u0014\u001a\u00020\u00152\u0018\u0010\u0016\u001a\u0014\u0012\u0004\u0012\u00020\u0012\u0012\u0004\u0012\u00020\u0012\u0012\u0004\u0012\u00020\u00010\u0017H\u0007\u001a\u0010\u0010\u0018\u001a\u00020\t2\u0006\u0010\u0019\u001a\u00020\u001aH\u0002\u001a(\u0010\u001b\u001a\u00020\t2\u0006\u0010\u001c\u001a\u00020\u00122\u0006\u0010\u001d\u001a\u00020\u00122\u0006\u0010\u001e\u001a\u00020\u00122\u0006\u0010\u001f\u001a\u00020\u0012H\u0002\u00a8\u0006 "}, d2 = {"AnimatedVisibility", "", "visible", "", "content", "Lkotlin/Function0;", "Landroidx/compose/runtime/Composable;", "DayChip", "label", "", "isSelected", "onClick", "ScheduleScreen", "viewModel", "Lcom/travlytic/app/ui/viewmodel/MainViewModel;", "onNavigateBack", "TimePickerButton", "hour", "", "minute", "context", "Landroid/content/Context;", "onTimePicked", "Lkotlin/Function2;", "buildScheduleSummary", "state", "Lcom/travlytic/app/ui/viewmodel/ScheduleState;", "calculateDuration", "sh", "sm", "eh", "em", "app_debug"})
public final class ScheduleScreenKt {
    
    @kotlin.OptIn(markerClass = {androidx.compose.material3.ExperimentalMaterial3Api.class})
    @androidx.compose.runtime.Composable()
    public static final void ScheduleScreen(@org.jetbrains.annotations.NotNull()
    com.travlytic.app.ui.viewmodel.MainViewModel viewModel, @org.jetbrains.annotations.NotNull()
    kotlin.jvm.functions.Function0<kotlin.Unit> onNavigateBack) {
    }
    
    @androidx.compose.runtime.Composable()
    public static final void DayChip(@org.jetbrains.annotations.NotNull()
    java.lang.String label, boolean isSelected, @org.jetbrains.annotations.NotNull()
    kotlin.jvm.functions.Function0<kotlin.Unit> onClick) {
    }
    
    @androidx.compose.runtime.Composable()
    public static final void TimePickerButton(@org.jetbrains.annotations.NotNull()
    java.lang.String label, int hour, int minute, @org.jetbrains.annotations.NotNull()
    android.content.Context context, @org.jetbrains.annotations.NotNull()
    kotlin.jvm.functions.Function2<? super java.lang.Integer, ? super java.lang.Integer, kotlin.Unit> onTimePicked) {
    }
    
    private static final java.lang.String calculateDuration(int sh, int sm, int eh, int em) {
        return null;
    }
    
    private static final java.lang.String buildScheduleSummary(com.travlytic.app.ui.viewmodel.ScheduleState state) {
        return null;
    }
    
    @androidx.compose.runtime.Composable()
    private static final void AnimatedVisibility(boolean visible, kotlin.jvm.functions.Function0<kotlin.Unit> content) {
    }
}