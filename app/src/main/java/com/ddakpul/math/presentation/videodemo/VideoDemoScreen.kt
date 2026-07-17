package com.ddakpul.math.presentation.videodemo

import androidx.compose.foundation.layout.Arrangement
import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.Row
import androidx.compose.foundation.layout.aspectRatio
import androidx.compose.foundation.layout.fillMaxSize
import androidx.compose.foundation.layout.fillMaxWidth
import androidx.compose.foundation.layout.padding
import androidx.compose.foundation.layout.widthIn
import androidx.compose.foundation.rememberScrollState
import androidx.compose.foundation.verticalScroll
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.automirrored.filled.ArrowBack
import androidx.compose.material3.Card
import androidx.compose.material3.FilterChip
import androidx.compose.material3.Icon
import androidx.compose.material3.IconButton
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.Text
import androidx.compose.runtime.Composable
import androidx.compose.runtime.DisposableEffect
import androidx.compose.runtime.LaunchedEffect
import androidx.compose.runtime.getValue
import androidx.compose.runtime.mutableIntStateOf
import androidx.compose.runtime.remember
import androidx.compose.runtime.setValue
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.platform.LocalContext
import androidx.compose.ui.res.stringResource
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.unit.dp
import androidx.compose.ui.viewinterop.AndroidView
import androidx.media3.common.MediaItem
import androidx.media3.exoplayer.ExoPlayer
import androidx.media3.ui.PlayerView
import com.ddakpul.math.R

/** 미리보기 영상은 프로토타입이라 앱에 동봉한다. 정식 기능에서는 서버(R2) 온디맨드 다운로드로 전환. */
private data class DemoVideo(
    val uri: String,
    val pickLabelRes: Int,
    val problemLabelRes: Int,
    val statementRes: Int,
)

private val DEMO_VIDEOS =
    listOf(
        DemoVideo(
            uri = "asset:///videos/demo_gridtilt.mp4",
            pickLabelRes = R.string.video_demo_pick1,
            problemLabelRes = R.string.video_demo_problem_label,
            statementRes = R.string.video_demo_statement,
        ),
        DemoVideo(
            uri = "asset:///videos/demo_nim.mp4",
            pickLabelRes = R.string.video_demo_pick2,
            problemLabelRes = R.string.video_demo_problem_label2,
            statementRes = R.string.video_demo_statement2,
        ),
    )

/**
 * 동영상 해설 품질 평가용 미리보기 화면 (베타).
 *
 * 대표 문제와 그 해설 영상을 페어로 보여 준다 — 정식 기능의 UX는 풀이 화면에
 * '동영상 풀이 보기' 버튼이 붙는 형태이고, 이 화면은 평가 전용 진입점이다.
 */
@Composable
fun VideoDemoScreen(
    onBack: () -> Unit,
    modifier: Modifier = Modifier,
) {
    var selected by remember { mutableIntStateOf(0) }
    val video = DEMO_VIDEOS[selected]

    Column(
        modifier = modifier.fillMaxSize().verticalScroll(rememberScrollState()).padding(24.dp),
        verticalArrangement = Arrangement.spacedBy(16.dp),
        horizontalAlignment = Alignment.CenterHorizontally,
    ) {
        Column(
            modifier = Modifier.widthIn(max = 720.dp).fillMaxWidth(),
            verticalArrangement = Arrangement.spacedBy(16.dp),
        ) {
            IconButton(onClick = onBack) {
                Icon(
                    imageVector = Icons.AutoMirrored.Filled.ArrowBack,
                    contentDescription = stringResource(R.string.video_demo_back),
                )
            }
            Text(
                text = stringResource(R.string.video_demo_title),
                style = MaterialTheme.typography.headlineMedium,
                fontWeight = FontWeight.Bold,
            )

            Row(horizontalArrangement = Arrangement.spacedBy(8.dp)) {
                DEMO_VIDEOS.forEachIndexed { index, item ->
                    FilterChip(
                        selected = selected == index,
                        onClick = { selected = index },
                        label = { Text(stringResource(item.pickLabelRes)) },
                    )
                }
            }

            Card {
                Column(
                    modifier = Modifier.padding(20.dp),
                    verticalArrangement = Arrangement.spacedBy(8.dp),
                ) {
                    Text(
                        text = stringResource(video.problemLabelRes),
                        style = MaterialTheme.typography.labelLarge,
                        color = MaterialTheme.colorScheme.primary,
                    )
                    Text(
                        text = stringResource(video.statementRes),
                        style = MaterialTheme.typography.bodyLarge,
                    )
                }
            }

            DemoVideoPlayer(
                uri = video.uri,
                modifier = Modifier.fillMaxWidth().aspectRatio(16f / 9f),
            )

            Text(
                text = stringResource(R.string.video_demo_note),
                style = MaterialTheme.typography.bodyMedium,
                color = MaterialTheme.colorScheme.onSurfaceVariant,
            )
        }
    }
}

@Composable
private fun DemoVideoPlayer(
    uri: String,
    modifier: Modifier = Modifier,
) {
    val context = LocalContext.current
    val player = remember { ExoPlayer.Builder(context).build() }
    LaunchedEffect(uri) {
        player.setMediaItem(MediaItem.fromUri(uri))
        player.prepare()
    }
    DisposableEffect(Unit) {
        onDispose { player.release() }
    }
    AndroidView(
        modifier = modifier,
        factory = { ctx -> PlayerView(ctx).apply { this.player = player } },
    )
}
