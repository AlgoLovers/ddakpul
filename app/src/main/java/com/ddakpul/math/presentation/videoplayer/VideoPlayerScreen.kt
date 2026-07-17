package com.ddakpul.math.presentation.videoplayer

import androidx.compose.foundation.layout.Arrangement
import androidx.compose.foundation.layout.Box
import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.aspectRatio
import androidx.compose.foundation.layout.fillMaxSize
import androidx.compose.foundation.layout.fillMaxWidth
import androidx.compose.foundation.layout.padding
import androidx.compose.foundation.layout.widthIn
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.automirrored.filled.ArrowBack
import androidx.compose.material3.CircularProgressIndicator
import androidx.compose.material3.Icon
import androidx.compose.material3.IconButton
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.OutlinedButton
import androidx.compose.material3.Surface
import androidx.compose.material3.Text
import androidx.compose.runtime.Composable
import androidx.compose.runtime.DisposableEffect
import androidx.compose.runtime.LaunchedEffect
import androidx.compose.runtime.getValue
import androidx.compose.runtime.remember
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.platform.LocalContext
import androidx.compose.ui.res.stringResource
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.unit.dp
import androidx.compose.ui.viewinterop.AndroidView
import androidx.hilt.navigation.compose.hiltViewModel
import androidx.lifecycle.compose.collectAsStateWithLifecycle
import androidx.media3.common.MediaItem
import androidx.media3.exoplayer.ExoPlayer
import androidx.media3.ui.PlayerView
import com.ddakpul.math.R

/**
 * 해설 영상 화면 — 캐시돼 있으면 즉시, 아니면 1회 내려받은 뒤 재생한다(이후 오프라인 재생).
 * 영상 파일은 APK에 없다 — 방법코드 기준으로 서버에서 받아 버전 캐시.
 */
@Composable
fun VideoPlayerScreen(
    methodCode: String,
    title: String,
    onBack: () -> Unit,
    modifier: Modifier = Modifier,
    viewModel: VideoPlayerViewModel = hiltViewModel(),
) {
    val state by viewModel.state.collectAsStateWithLifecycle()
    LaunchedEffect(methodCode) { viewModel.load(methodCode) }

    Column(
        modifier = modifier.fillMaxSize().padding(20.dp),
        verticalArrangement = Arrangement.spacedBy(16.dp),
        horizontalAlignment = Alignment.CenterHorizontally,
    ) {
        Column(
            modifier = Modifier.widthIn(max = 720.dp).fillMaxWidth(),
            verticalArrangement = Arrangement.spacedBy(12.dp),
        ) {
            IconButton(onClick = onBack) {
                Icon(
                    imageVector = Icons.AutoMirrored.Filled.ArrowBack,
                    contentDescription = stringResource(R.string.video_player_back),
                )
            }
            Text(
                text = title,
                style = MaterialTheme.typography.headlineSmall,
                fontWeight = FontWeight.Bold,
            )
            VideoStage(
                state = state,
                onRetry = { viewModel.load(methodCode) },
                modifier = Modifier.fillMaxWidth().aspectRatio(16f / 9f),
            )
        }
    }
}

@Composable
private fun VideoStage(
    state: VideoPlayerState,
    onRetry: () -> Unit,
    modifier: Modifier = Modifier,
) {
    Surface(
        modifier = modifier,
        color = MaterialTheme.colorScheme.surfaceContainerHigh,
    ) {
        when (state) {
            is VideoPlayerState.Ready -> {
                VideoSurface(uri = state.fileUri, modifier = Modifier.fillMaxSize())
            }

            is VideoPlayerState.Downloading -> {
                CenterBox {
                    CircularProgressIndicator()
                    Text(
                        text = stringResource(R.string.video_downloading, state.percent),
                        style = MaterialTheme.typography.bodyMedium,
                    )
                }
            }

            VideoPlayerState.Loading -> {
                CenterBox { CircularProgressIndicator() }
            }

            VideoPlayerState.Failed -> {
                CenterBox {
                    Text(
                        text = stringResource(R.string.video_download_failed),
                        style = MaterialTheme.typography.bodyMedium,
                    )
                    OutlinedButton(onClick = onRetry) {
                        Text(stringResource(R.string.video_retry))
                    }
                }
            }
        }
    }
}

@Composable
private fun CenterBox(content: @Composable () -> Unit) {
    Box(modifier = Modifier.fillMaxSize(), contentAlignment = Alignment.Center) {
        Column(
            horizontalAlignment = Alignment.CenterHorizontally,
            verticalArrangement = Arrangement.spacedBy(12.dp),
        ) {
            content()
        }
    }
}

@Composable
private fun VideoSurface(
    uri: String,
    modifier: Modifier = Modifier,
) {
    val context = LocalContext.current
    val player = remember { ExoPlayer.Builder(context).build() }
    LaunchedEffect(uri) {
        player.setMediaItem(MediaItem.fromUri(uri))
        player.prepare()
        player.playWhenReady = true
    }
    DisposableEffect(Unit) {
        onDispose { player.release() }
    }
    AndroidView(
        modifier = modifier,
        factory = { ctx -> PlayerView(ctx).apply { this.player = player } },
    )
}
