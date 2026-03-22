from aiogram import F, Router, types
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import CallbackQuery

from keyboards import Keyboards
from use_cases.display_user_goals_use_case import DisplayUserGoals
from use_cases.save_goal_use_case import SaveGoalUseCase


class GoalForm(StatesGroup):
    waiting_for_goal = State()
    waiting_for_taget = State()

class GoalHandler:
    def __init__(self, save_goal_us: SaveGoalUseCase, display_goals_us: DisplayUserGoals):
        self.save_goal_us = save_goal_us
        self.display_goals_us = display_goals_us
        self.router = Router()

    def register(self):
        @self.router.message(lambda message: message.text == "Цели")
        async def handle_goaks_button(message: types.Message):
            await message.answer("Выберите тип:", reply_markup=Keyboards.get_all_goals_buttons())

        @self.router.callback_query(F.data == "save_goal")
        async def handle_save_goal(callback: CallbackQuery, state: FSMContext):
            await callback.answer()
            await callback.message.answer("Напишите описание вашей цели")
            await state.set_state(GoalForm.waiting_for_goal)
            
        @self.router.message(GoalForm.waiting_for_goal)
        async def handle_goal_text(message: types.Message, state: FSMContext):
            await state.update_data(goal_description=message.text)

            await message.answer("Введите сколько денег планируете копить:")
            await state.set_state(GoalForm.waiting_for_taget)
            
        @self.router.message(GoalForm.waiting_for_taget)
        async def handle_goal_target(message: types.Message, state: FSMContext):
            data = await state.get_data()
            goal_text = data.get("goal_description")
            await state.clear()
            if not goal_text:
                await message.answer("анлак")
            await self.save_goal_us.execute(message.from_user.id, float(message.text), 0, goal_text)
        
        @self.router.callback_query(F.data == "del_goal")
        async def handle_del_goal(callback: CallbackQuery):
            await callback.answer()
        
        @self.router.callback_query(F.data == "set_up_goal")
        async def handle_set_up_goals(callback: CallbackQuery):
            await callback.answer()
            
        @self.router.callback_query(F.data == "display_goals")
        async def handle_set_up_goals(callback: CallbackQuery):
            await callback.answer()
            data = await self.display_goals_us.execute(callback.from_user.id)
            output = ""
            for index, goal in enumerate(data):
                output += f"<b>{index + 1}. {goal[0]}, изначальная цель {goal[1]}\n</b>"
                
            await callback.message.answer(
                f"Вот список ваших целей:\n{output}",
                parse_mode="HTML"
                )
