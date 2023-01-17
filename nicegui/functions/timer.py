import asyncio
import time
import traceback
from typing import Callable

from .. import background_tasks, globals
from ..async_updater import AsyncUpdater
from ..binding import BindableProperty
from ..helpers import is_coroutine


class Timer:
    active = BindableProperty()
    interval = BindableProperty()

    def __init__(self, interval: float, callback: Callable, *, active: bool = True, once: bool = False) -> None:
        """Timer

        One major drive behind the creation of NiceGUI was the necessity to have a simple approach to update the interface in regular intervals,
        for example to show a graph with incoming measurements.
        A timer will execute a callback repeatedly with a given interval.

        :param interval: the interval in which the timer is called (can be changed during runtime)
        :param callback: function or coroutine to execute when interval elapses
        :param active: whether the callback should be executed or not (can be changed during runtime)
        :param once: whether the callback is only executed once after a delay specified by `interval` (default: `False`)
        """
        self.interval = interval
        self.callback = callback
        self.active = active
        self.slot = globals.get_slot()

        coroutine = self._run_once if once else self._run_in_loop
        if globals.state == globals.State.STARTED:
            background_tasks.create(coroutine(), name=str(callback))
        else:
            globals.app.on_startup(coroutine)

    async def _run_once(self) -> None:
        try:
            with self.slot:
                await self._connected()
                await asyncio.sleep(self.interval)
                if globals.state not in [globals.State.STOPPING, globals.State.STOPPED]:
                    await self._invoke_callback()
        finally:
            self.cleanup()

    async def _run_in_loop(self) -> None:
        try:
            with self.slot:
                await self._connected()
                while True:
                    if self.slot.parent.client.id not in globals.clients:
                        break
                    if globals.state in [globals.State.STOPPING, globals.State.STOPPED]:
                        break
                    try:
                        start = time.time()
                        if self.active:
                            await self._invoke_callback()
                        dt = time.time() - start
                        await asyncio.sleep(self.interval - dt)
                    except asyncio.CancelledError:
                        break
                    except:
                        globals.log.exception('Exception in timer callback')
                        await asyncio.sleep(self.interval)
        finally:
            self.cleanup()

    async def _invoke_callback(self) -> None:
        try:
            result = self.callback()
            if is_coroutine(self.callback):
                await AsyncUpdater(result)
        except Exception:
            traceback.print_exc()

    async def _connected(self) -> None:
        '''Wait for the client connection before the timer callback can can be allowed to manipulate the state.
        See https://github.com/zauberzeug/nicegui/issues/206 for details.
        '''
        if not self.slot.parent.client.shared:
            await self.slot.parent.client.connected()

    def cleanup(self) -> None:
        self.slot = None
        self.callback = None
