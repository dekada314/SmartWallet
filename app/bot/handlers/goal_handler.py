from io import BytesIO

import matplotlib.patches as patches
import matplotlib.pyplot as plt
from aiogram import F, Router, types
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import BufferedInputFile, CallbackQuery

from app.bot.keyboards.keyboards import Keyboards
from app.bot.middleware.goal_middleware import GoalMiddleware
from app.dto.requests.del_goal_request import DelGoalRequest
from app.dto.requests.save_goal_request import SaveGoalRequest
from application.use_cases.change_goal_desc_use_case import ChangeGoalDescUseCase
from application.use_cases.delete_goal_use_case import DeleteGoalUseCase
from application.use_cases.display_user_goals_use_case import DisplayUserGoals
from application.use_cases.exceeding_the_limit_use_case import ExceedingTheLimitUseCase
from application.use_cases.save_goal_use_case import SaveGoalUseCase
from application.use_cases.update_goal_use_case import UpdateGoalUseCase
from domain.entities.goal import Goal


class GoalForm(StatesGroup):
    waiting_for_goal = State()
    waiting_for_taget = State()
    waiting_for_update = State()
    waiting_for_new_desc = State()


class GoalHandler:
    def __init__(
        self,
        save_goal_us: SaveGoalUseCase,
        display_goals_us: DisplayUserGoals,
        update_goal_us: UpdateGoalUseCase,
        delete_goal_us: DeleteGoalUseCase,
        change_goal_us: ChangeGoalDescUseCase,
        exceeding_the_limits_us: ExceedingTheLimitUseCase,
    ):
        self.save_goal_us = save_goal_us
        self.display_goals_us = display_goals_us
        self.update_goal_us = update_goal_us
        self.delete_goal_us = delete_goal_us
        self.change_goal_us = change_goal_us
        self.exceeding_the_limits_us = exceeding_the_limits_us
        self.router = Router(name="goal_router")

    def register(self):
        self.router.message.middleware(GoalMiddleware())
        self.router.callback_query.middleware(GoalMiddleware())

        def _progress_donut(
            current, total, title: str = "Процесс накопления"
        ) -> BytesIO:
            percent = (current / total) * 100
            remaining = 100 - percent

            fig, ax = plt.subplots(figsize=(6, 4))

            sizes = [percent, remaining]
            colors = ["#2ecc71", "#ecf0f1"]
            labels = [f"Накоплено: {percent:.1f}%", f"Осталось: {remaining:.1f}%"]

            wedges, texts, autotexts = ax.pie(
                sizes,
                labels=labels,
                colors=colors,
                autopct="%1.1f%%",
                startangle=90,
                wedgeprops={"edgecolor": "white", "linewidth": 2},
            )

            centre_circle = plt.Circle((0, 0), 0.70, fc="white", linewidth=0)
            fig.gca().add_artist(centre_circle)

            plt.text(
                0,
                0,
                f"{current:,}\n/\n{total:,}",
                ha="center",
                va="center",
                fontsize=14,
                fontweight="bold",
            )

            ax.set_title(title, fontsize=14, pad=20)
            ax.axis("equal")

            bio = BytesIO()
            plt.savefig(bio, format="png", dpi=100, bbox_inches="tight")
            bio.seek(0)
            plt.close()

            return bio

        @self.router.message(lambda message: message.text == "Цели")
        async def handle_goaks_button(message: types.Message):
            await message.answer(
                "Выберите тип:", reply_markup=Keyboards.get_all_goals_buttons()
            )

        @self.router.callback_query(F.data == "save_goal")
        async def handle_save_goal(callback: CallbackQuery, state: FSMContext):
            await callback.answer()
            if await self.exceeding_the_limits_us.execute(callback.from_user.id):
                await callback.message.answer("Напишите описание вашей цели:")
                await state.set_state(GoalForm.waiting_for_goal)
            else:
                await callback.message.answer(
                    "У вас уже целых 5 целей, предлагаю пока что сфокусироваться на уже существующих"
                )

        @self.router.message(GoalForm.waiting_for_goal)
        async def handle_goal_text(message: types.Message, state: FSMContext):
            await state.update_data(goal_description=message.text)

            await message.answer("Записал!")
            await message.answer("Теперь введите сколько денег планируете копить:")
            await state.set_state(GoalForm.waiting_for_taget)

        @self.router.message(GoalForm.waiting_for_taget)
        async def handle_goal_target(message: types.Message, state: FSMContext):
            data = await state.get_data()
            goal_text = data.get("goal_description")
            await state.clear()
            save_goal_request = SaveGoalRequest(
                user_id=message.from_user.id, amount=message.text, text=goal_text
            )
            goal = await self.save_goal_us.execute(save_goal_request)
            if goal:
                await message.answer("Цель успешно сохранена!")
            else:
                await message.answer("Значения введены неверно, попробуйте снова")

        @self.router.callback_query(F.data == "set_up_goal")
        async def handle_set_up_goals(callback: CallbackQuery, state: FSMContext):
            await callback.answer()
            data = await self.display_goals_us.execute(callback.from_user.id)

            await callback.message.answer("Вот все ваши цели для настройки:")

            for index, goal in enumerate(data):
                await state.update_data(goal_text=goal.text)
                await callback.message.answer(
                    f"<b>{index + 1}. {goal.text}\n</b>Ваш прогресс по этой цели:\n",
                    parse_mode="HTML",
                )

                progress_chart = _progress_donut(goal.curr_bill, goal.target)
                photo_file = BufferedInputFile(progress_chart.getvalue(), "Прогресс по цели")

                if photo_file:
                    await callback.message.answer_photo(
                        photo=photo_file,
                        reply_markup=Keyboards.get_setup_goal_button(
                            str(goal.order_number)
                        ),
                    )

        @self.router.callback_query(F.data.startswith("del_goal_"))
        async def handle_delete_goal(callback: CallbackQuery):
            await callback.answer()
            order_number = int(callback.data.split("del_goal_")[1])

            del_goal_request = DelGoalRequest(
                user_id=callback.from_user.id, order_number=order_number
            )

            goal = await self.delete_goal_us.execute(del_goal_request)

            if goal:
                await callback.message.answer("Цель успешно удалена")

        @self.router.callback_query(F.data.startswith("update_desc_"))
        async def handle_change_desc(callback: CallbackQuery, state: FSMContext):
            await callback.answer()
            order_number = int(callback.data.split("update_desc_")[1])
            await state.update_data(order_number=order_number)
            await callback.message.answer("Введите новое описание цели:")
            await state.set_state(GoalForm.waiting_for_new_desc)

        @self.router.message(GoalForm.waiting_for_new_desc)
        async def change_desc(message: types.Message, state: FSMContext):
            data = await state.get_data()
            order_number = data.get("order_number")
            goal = await self.change_goal_us.execute(message, order_number)
            if goal:
                await message.answer("Описание цели было успешно изменено!")
            await state.clear()

        @self.router.callback_query(F.data == "display_goals")
        async def handle_set_up_goals(callback: CallbackQuery, state: FSMContext):
            await callback.answer()
            data = await self.display_goals_us.execute(callback.from_user.id)

            if not data:
                await callback.message.answer("Ваш список целей пока что пуст!")
            else:
                await callback.message.answer("Вот все ваши цели:")

                for index, goal in enumerate(data):
                    await state.update_data(goal_text=goal.text)
                    await callback.message.answer(
                        f"<b>{index + 1}. {goal.text}\n</b>Ваш прогресс по этой цели:\n",
                        parse_mode="HTML",
                    )

                    progress_chart = _progress_donut(goal.curr_bill, goal.target)
                    photo_file = BufferedInputFile(progress_chart.getvalue(), "Прогресс по цели")

                    if photo_file:
                        await callback.message.answer_photo(
                            photo=photo_file,
                            reply_markup=Keyboards.get_update_goal_button(
                                str(goal.order_number)
                            ),
                        )

        @self.router.callback_query(F.data.startswith("update_goal_"))
        async def update_goal(callback: CallbackQuery, state: FSMContext):
            await callback.answer()
            user_goal_num = int(callback.data.split("update_goal_")[1])
            await state.update_data(goal_id=user_goal_num)
            await callback.message.answer("Введите сколько хотите внести в цель")
            await state.set_state(GoalForm.waiting_for_update)

        @self.router.message(GoalForm.waiting_for_update)
        async def handle_update_goal(message: types.Message, state: FSMContext):
            data = await state.get_data()
            goal_id = data.get("goal_id")
            goal_callback = await self.update_goal_us.execute(message, goal_id)

            if isinstance(goal_callback, Goal):
                await message.answer("Ваши накопления записаны")
            elif goal_callback == 0:
                await message.answer(
                    "Ого, как вы точно расчитали! Цель <b>идеально</b> выполнена",
                    parse_mode="HTML",
                )
            elif goal_callback > 0:
                await message.answer(
                    f"Поздравляю! Вы выполнили свою цель!!! И даже перевыполнили на {goal_callback}"
                )
            else:
                await message.answer("Кажется вы что-то не так ввели")
