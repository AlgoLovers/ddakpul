package com.ddakpul.math.presentation.settings

import androidx.lifecycle.ViewModel
import androidx.lifecycle.viewModelScope
import com.ddakpul.math.domain.usecase.ResetProgressUseCase
import dagger.hilt.android.lifecycle.HiltViewModel
import kotlinx.coroutines.launch
import javax.inject.Inject

@HiltViewModel
class SettingsViewModel
    @Inject
    constructor(
        private val resetProgress: ResetProgressUseCase,
    ) : ViewModel() {
        fun resetProgress() {
            viewModelScope.launch { resetProgress.invoke() }
        }
    }
